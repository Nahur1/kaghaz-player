"""Publish a tested Actions build without exposing incomplete update assets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def version_parts(value):
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError(f"Expected a stable X.Y.Z version, got {value!r}")
    return tuple(map(int, value.split(".")))


def verify_assets(directory, repository):
    directory = Path(directory)
    manifest = json.loads((directory / "latest.json").read_text(encoding="utf-8-sig"))
    version = manifest["version"]
    version_parts(version)
    installer = directory / f"kaghaz-setup-{version}.exe"
    expected = f"https://github.com/{repository}/releases/download/v{version}/{installer.name}"
    if manifest["url"] != expected:
        raise ValueError("Update manifest points to an unexpected repository or version")
    digest = hashlib.sha256(installer.read_bytes()).hexdigest()
    if not re.fullmatch(r"[a-f0-9]{64}", manifest["sha256"]) or digest != manifest["sha256"]:
        raise ValueError("Installer checksum does not match latest.json")
    if installer.stat().st_size == 0:
        raise ValueError("Installer is empty")
    return version, installer


def release_plan(version, commit, main_commit, existing, latest):
    if commit != main_commit:
        return "skip: a newer main commit is waiting to build"
    if existing and not existing["draft"]:
        return "skip: this version is already published; increase Cargo.toml version for the next update"
    if latest and version_parts(latest["tag_name"].removeprefix("v")) >= version_parts(version):
        return "skip: a release at this version or newer is already latest"
    if existing and existing["target_commitish"] != commit:
        raise ValueError("An existing draft belongs to a different commit; refusing to overwrite it")
    return "publish"


def gh(*args, optional=False):
    result = subprocess.run(["gh", *args], text=True, encoding="utf-8", capture_output=True)
    if result.returncode:
        if optional and "HTTP 404" in result.stderr:
            return None
        raise RuntimeError(result.stderr.strip() or f"GitHub CLI exited {result.returncode}")
    return result.stdout


def api(path, optional=False):
    result = gh("api", path, optional=optional)
    return json.loads(result) if result is not None else None


def tagged_release(base, tag):
    # The by-tag endpoint only promises published releases. Authenticated lists
    # also include drafts, which lets a failed upload be resumed safely.
    pages = json.loads(gh("api", "--paginate", "--slurp", f"{base}/releases?per_page=100"))
    return next((release for page in pages for release in page if release["tag_name"] == tag), None)


def summary(message):
    print(message)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as output:
            output.write(message + "\n")


def publish(directory, repository, commit):
    if repository != "Nahur1/kaghaz-player" or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Publishing requires the official repository and a full commit SHA")
    version, installer = verify_assets(directory, repository)
    declared = re.search(r'^version = "([^"]+)"', Path("Cargo.toml").read_text(encoding="utf-8"), re.MULTILINE)
    if not declared or version != declared.group(1):
        raise ValueError("Build artifacts do not match the checked-out package version")
    tag = f"v{version}"
    base = f"repos/{repository}"
    main_commit = api(f"{base}/git/ref/heads/main")["object"]["sha"]
    existing = tagged_release(base, tag)
    latest = api(f"{base}/releases/latest", optional=True)
    plan = release_plan(version, commit, main_commit, existing, latest)
    if plan != "publish":
        summary(plan)
        return
    # Keep the release private until both update files have been uploaded.
    if not existing:
        args = ["release", "create", tag, "--repo", repository, "--target", commit,
                "--draft", "--title", f"Kaghaz Player {version}"]
        notes = Path("docs/releases") / f"{version}.md"
        args += ["--notes-file", str(notes)] if notes.is_file() else ["--generate-notes"]
        gh(*args)
        existing = tagged_release(base, tag)
        if existing is None:
            raise ValueError("Created draft release could not be found")
    gh("release", "upload", tag, str(installer), str(Path(directory) / "latest.json"),
       "--repo", repository, "--clobber")
    draft = api(f"{base}/releases/{existing['id']}")
    assets = {asset["name"]: asset["size"] for asset in draft["assets"]}
    for path in [installer, Path(directory) / "latest.json"]:
        if assets.get(path.name) != path.stat().st_size:
            raise ValueError(f"Release upload missing or incomplete: {path.name}")
    # Recheck after uploads: a different build must not become latest behind us.
    main_commit = api(f"{base}/git/ref/heads/main")["object"]["sha"]
    latest = api(f"{base}/releases/latest", optional=True)
    plan = release_plan(version, commit, main_commit, draft, latest)
    if plan != "publish":
        summary(plan + "; the unpublished draft is retained")
        return
    gh("release", "edit", tag, "--repo", repository, "--draft=false", "--latest")
    published = api(f"{base}/releases/latest")
    if published["tag_name"] != tag or published["draft"]:
        raise ValueError("Release did not become the latest public version")
    summary(f"Published [{tag}](https://github.com/{repository}/releases/tag/{tag}) with verified update assets.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    publish(args.artifact_dir, args.repository, args.commit)
