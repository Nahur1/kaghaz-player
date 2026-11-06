# Attribution and bundled components

Kaghaz Player is an independent derivative of [Nava](https://github.com/reza-hashemian/nava) by Reza Hashemian. The original MIT license is retained in LICENSE. Nava supplies the player architecture, glass interface, icons and music library functionality.

Live translation uses the English→Persian model (version 1.1) from Mozilla's [Firefox Translations](https://github.com/mozilla/firefox-translations-models), under the Mozilla Public License 2.0; its notice is in `models/enfa/LICENSE.txt`. The model is run by Kaghaz's own Rust code, written from the published Marian model format; no Mozilla or Marian code is included. Checksums are pinned in `src/subtitles.rs` and `scripts/prepare-offline.py`.

[Vazirmatn](https://github.com/rastikerdar/vazirmatn) by the Vazirmatn Project Authors and [Inter](https://rsms.me/inter/) are distributed under the SIL Open Font License. Their license files are in `ui/fonts` and the portable app's `runtime/fonts` folder.

Playback uses libmpv; FFmpeg is optional (reading embedded tracks ahead) and is not bundled by default. The development/portable build on this machine reuses the existing Nava libmpv DLL. These binaries can have GPL components. Before publicly distributing binaries, supply the exact corresponding source and all applicable license notices, or rebuild compatible components under suitable terms. See [mpv copyright](https://github.com/mpv-player/mpv/blob/master/Copyright) and [FFmpeg legal](https://ffmpeg.org/legal.html). Local source use and the provided private build do not publish any files.

Slint has its own licensing terms: [Slint licensing](https://slint.dev/license). Review these and dependency licenses before commercial distribution.
