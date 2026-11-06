"""Exercise the real Windows player using an isolated profile and local IPC."""
import argparse
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import wave


def run(exe):
    exe = Path(exe).resolve(strict=True)
    if exe.with_name("unins000.exe").exists():
        raise ValueError("Use a portable/test executable, not an installed application")
    with tempfile.TemporaryDirectory(prefix="kaghaz-smoke-") as directory:
        root = Path(directory).resolve()
        assert root.parent == Path(tempfile.gettempdir()).resolve()
        audio = root / "smoke.wav"
        with wave.open(str(audio), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(8000)
            output.writeframes(b"\0" * (8000 * 2 * 90))
        env = os.environ.copy()
        env.update(KAGHAZ_PROFILE_DIR=str(root / "profile"), KAGHAZ_RENDERER="software", KAGHAZ_AO="null")
        env.pop("KAGHAZ_MINI", None)
        env.pop("KAGHAZ_RELAUNCHED", None)
        processes = []
        with open(root / "output.log", "w", encoding="utf-8") as log:
            try:
                def launch():
                    with socket.socket() as probe:
                        probe.bind(("127.0.0.1", 0))
                        port = probe.getsockname()[1]
                    env["KAGHAZ_IPC_PORT"] = str(port)
                    process = subprocess.Popen([str(exe), str(audio)], env=env, stdout=log, stderr=log)
                    processes.append(process)

                    def send(*parts):
                        with socket.create_connection(("127.0.0.1", port), timeout=2) as stream:
                            stream.sendall(("\t".join(parts) + "\n").encode())
                            return stream.recv(4096).decode("utf-8").strip()

                    def expect(value):
                        deadline = time.monotonic() + 20
                        while time.monotonic() < deadline:
                            if process.poll() is not None:
                                raise AssertionError(f"Player exited unexpectedly: {process.returncode}")
                            try:
                                result = send("status", "{volume}|{muted}|{mini}")
                                if result == value:
                                    return
                            except OSError:
                                pass
                            time.sleep(0.1)
                        raise AssertionError(f"Player did not reach expected state {value!r}")

                    def close():
                        try:
                            send("close")
                        except (ConnectionResetError, BrokenPipeError):
                            pass  # The process can exit before its final reply.
                        assert process.wait(timeout=10) == 0, "Player did not exit cleanly"
                        try:
                            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                                raise AssertionError("IPC listener survived closing the player")
                        except (ConnectionRefusedError, TimeoutError):
                            pass

                    return send, expect, close

                send, expect, close = launch()
                expect("80|no|no")
                send("mute")
                expect("80|yes|no")
                send("mini")
                expect("80|yes|yes")
                send("mute")
                expect("80|no|yes")
                send("full")
                expect("80|no|no")
                send("mute")
                expect("80|yes|no")
                close()
                send, expect, close = launch()
                expect("80|yes|no")  # Mute and volume survive a full process restart.
                close()
                print("PASS: native mute/restore, mini/full transitions, persisted mute, complete process exit and released IPC port")
            except Exception:
                log.flush()
                print((root / "output.log").read_text(encoding="utf-8", errors="replace"))
                raise
            finally:
                for process in processes:
                    if process.poll() is None:
                        process.terminate()  # Only children created here, with isolated data.
                        process.wait(timeout=10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True)
    run(parser.parse_args().exe)
