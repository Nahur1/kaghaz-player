import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("publisher", Path(__file__).parents[1] / "publish-release.py")
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class ReleaseTests(unittest.TestCase):
    def test_verified_assets_and_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            installer = root / "kaghaz-setup-0.3.4.exe"
            installer.write_bytes(b"installer fixture")
            manifest = dict(version="0.3.4", sha256=hashlib.sha256(installer.read_bytes()).hexdigest(),
                            url="https://github.com/Nahur1/kaghaz-player/releases/download/v0.3.4/kaghaz-setup-0.3.4.exe")
            (root / "latest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(publisher.verify_assets(root, "Nahur1/kaghaz-player")[0], "0.3.4")
            installer.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                publisher.verify_assets(root, "Nahur1/kaghaz-player")

    def test_wrong_repository_and_path_versions(self):
        for value in ["../0.3.4", "0.3.4-beta", "v0.3.4", "1.2"]:
            with self.assertRaises(ValueError):
                publisher.version_parts(value)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "latest.json").write_text(json.dumps(dict(version="0.3.4", sha256="0" * 64, url="https://example.com/installer")))
            with self.assertRaises(ValueError):
                publisher.verify_assets(root, "Nahur1/kaghaz-player")

    def test_new_release_and_retry_same_draft(self):
        latest = dict(tag_name="v0.3.3")
        self.assertEqual(publisher.release_plan("0.3.4", "a", "a", None, latest), "publish")
        draft = dict(draft=True, target_commitish="a")
        self.assertEqual(publisher.release_plan("0.3.4", "a", "a", draft, latest), "publish")

    def test_published_assets_never_overwritten(self):
        plan = publisher.release_plan("0.3.4", "a", "a", dict(draft=False), None)
        self.assertTrue(plan.startswith("skip:"))

    def test_old_build_never_replaces_newer_release(self):
        self.assertTrue(publisher.release_plan("0.3.4", "a", "a", None, dict(tag_name="v0.3.5")).startswith("skip:"))
        self.assertTrue(publisher.release_plan("0.3.4", "a", "b", None, None).startswith("skip:"))

    def test_unrelated_draft_never_overwritten(self):
        with self.assertRaises(ValueError):
            publisher.release_plan("0.3.4", "a", "a", dict(draft=True, target_commitish="b"), None)


if __name__ == "__main__":
    unittest.main()
