# Kaghaz Player · کاغذ پلیر

By **Mohammad Fakhari (Nahur1)** · [Copyright and use conditions](COPYRIGHT.md).

An independent local music and video player with an Apple-inspired glass interface, built with Rust, Slint and libmpv. Window controls are at the upper right. The default Graphite palette matches the reference interface. Source origins and license notices are documented in [THIRD_PARTY.md](THIRD_PARTY.md) and [LICENSE](LICENSE).

[راهنمای فارسی](README.fa.md)

## Run on this Windows computer

Run `kaghaz-setup-0.3.4.exe` (from [Releases](https://github.com/Nahur1/kaghaz-player/releases) or `dist`). It installs for your user only, with no administrator prompt, adds Start menu and desktop shortcuts, and from then on Kaghaz keeps itself up to date automatically. The installed app is about 175 MB, the Persian model included.

A portable copy is also built in `dist/Kaghaz Player 0.3.4` (keep `libmpv-2.dll`, `runtime` and `models` beside `kaghaz.exe`); portable copies don't update themselves.

## Live Persian subtitles, offline

Open a film with English subtitles (embedded text track, a matching SRT/VTT/ASS next to it, or **Open SRT / VTT / ASS…**). Each line is translated the moment it appears and shown together with the original, in sync: in the test on this laptop the pair was on screen 2–11 ms after mpv showed the English line. Upcoming lines are translated ahead, and a sentence split over several cues is translated as one sentence.

- **T** cycles *Original → English + فارسی → فارسی*. The sparkle button in the video controls opens the full panel: mode, Persian line above or below, and size (Small / Medium / Large). Choices are remembered.
- With Persian on and no subtitle chosen, an English text track is picked automatically.
- **Save Persian SRT…** writes a complete Persian subtitle file (sentences merged into single cues, original timing kept). It never overwrites the source.
- Image subtitles (PGS/DVD) and non-English tracks are shown as they are, with a clear note.

The translator is Mozilla's Firefox Translations English→Persian model (22 MB, MPL-2.0), run by a small inference engine written in Rust inside Kaghaz (`src/mt.rs`, `src/spm.rs`): no server, no Python, no GPU required, about 10 ms per line on an ordinary CPU and ~70 MB of RAM. Common idioms and spoken contractions are rephrased before translation ("pulling my leg", "gonna"), and Persian half-spaces are fixed afterwards. Translation stays on the computer; the model is only downloaded once if it is missing (**Download model**, checksums verified). Machine translation can still miss jokes, names and ambiguous lines.

FFmpeg is optional. With it (in `runtime` or PATH), embedded tracks are also read ahead; without it, embedded tracks are translated line by line as they play, which is just as fast.

## Playback

Music library, albums, artists, favorites, sessions, equalizer and existing player features are retained. Video includes fullscreen (F), picture in picture, speed, seeking (arrows: 5 s, Shift+arrows: 1 s), frame stepping (`,` and `.`), subtitle/audio track selection and remembered playback position. V switches between the movie and library. Kaghaz uses its own `kaghaz` data/cache folders and Windows control port 47824, preserving data from earlier players.

## Build on Windows

Install stable Rust and MSVC C++ build tools/Windows SDK. Put `libmpv-2.dll` in `runtime`, and the fonts in `runtime/fonts` (copy `ui/fonts/*`).

```powershell
python scripts/prepare-offline.py   # fetch the pinned 22 MB Persian model into models/enfa
./scripts/build.ps1 -Test
./scripts/build.ps1 -Release
./scripts/package.ps1               # add -IncludeFFmpeg to bundle runtime/ffmpeg.exe (+230 MB)
```

Real-model checks (ignored by default): `./scripts/build.ps1 -Release -Test -Filter mt:: -Ignored` translates sample sentences; `-Filter render_overlay_frames -Ignored` opens a short mpv window and saves screenshots of the subtitle overlay to `test-results/frames`.

## Repository and credits

Source and releases: https://github.com/Nahur1/kaghaz-player.

## Releasing an update

Bump `version` in `Cargo.toml`, then run `./scripts/release.ps1 -Publish -Notes "What changed"` (needs Inno Setup 6 and the GitHub CLI). It builds `kaghaz-setup-X.Y.Z.exe` and `latest.json` and uploads both as a GitHub Release. Installed copies check about 20 seconds after start and every six hours, download the installer in the background, verify its SHA-256, and install it silently when Kaghaz closes (or straight away from About → Restart and update).

New original material covered by [LICENSE](LICENSE) is reserved to Mohammad Fakhari (Nahur1); copying or redistribution requires written permission except where expressly permitted. Earlier MIT material retains its permissions under [licenses/LEGACY-MIT.txt](licenses/LEGACY-MIT.txt). See [COPYRIGHT.md](COPYRIGHT.md) and [THIRD_PARTY.md](THIRD_PARTY.md) for scope and component terms.
