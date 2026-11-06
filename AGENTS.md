# Kaghaz Player project notes

## Preserve the owner's current baseline

The owner reviewed and adopted version 0.3.3. Preserve these changes unless a
new request explicitly changes them:

- The paper-P logo with its integrated play triangle, including app, window,
  taskbar, installer and Linux icons. Do not restore earlier logo proposals.
- Live offline English-to-Persian subtitles using the small Mozilla model and
  native Rust inference (`src/mt.rs`, `src/spm.rs`, `src/translator.rs`). Keep
  bilingual subtitle modes, prefetching, sentence merging and Persian settings.
  Do not restore the earlier Gemma/llama server architecture.
- Windows fullscreen repairs, including frame refresh and the temporary
  one-pixel resize that restores the GPU surface after leaving fullscreen.
- The stable installer AppId, updates over the existing installation, cleanup
  of older installation copies, preserved user settings and automatic updater.
- The existing Apple/macOS visual style, smooth playback progress, and the
  enlarged window controls at the top right with the owner's chosen order.

The active project is `D:\Kaghaz Player`, separate from MediaYar. Inspect the
working tree before editing; preserve uncommitted work and the `design/` folder.

## Commit identity and publication

- This owner's repository is https://github.com/Nahur1/kaghaz-player.
- Commits made on the owner's behalf must use the repository-local identity:
  `Nahur1 <51950495+Nahur1@users.noreply.github.com>` for author and committer.
- Never add AI identities, `Co-Authored-By` trailers, or override this identity
  with Codex/Claude names. Do not attribute another person's work to the owner;
  keep third-party license and copyright notices intact.
- `.githooks/commit-msg` and `.githooks/pre-push` enforce this local policy.
  For a fresh checkout, configure `git config --local core.hooksPath .githooks`,
  `user.name`, `user.email`, and `user.useConfigOnly true` before committing.
- Publish explicit refs. Local `main`, `nava-history`, and older upstream tags
  are historical backups and must not be pushed to this repository. Do not use
  `git push --all`, `--mirror`, or an unrestricted `--tags`.
- Attribution cleanup on 2026-11-06 preserved the exact file tree of all four
  v0.3.0-v0.3.3 releases. Original history is backed up locally under
  `.tools/attribution-backup-20261106-213253/`.
