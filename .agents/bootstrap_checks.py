"""Run one reviewed argv with local POSIX time/output bounds, not a sandbox."""

import hashlib
import os
import selectors
import signal
import subprocess
import time

MAX_OUTPUT = 1024 * 1024


def run_check(argv, root, env, timeout):
    result = {
        "status": "blocked",
        "exit_code": None,
        "output_sha256": None,
        "output_bytes": 0,
    }
    if os.name != "posix":
        return result | {
            "reason": "POSIX process groups required for local verification"
        }
    output = bytearray()
    process = None
    started = time.monotonic()
    try:
        # Only reviewed plan argv reaches this boundary; callers supply isolation.
        process = subprocess.Popen(
            argv,
            cwd=root,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            start_new_session=True,
            close_fds=True,
        )
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while selector.get_map():
                remaining = timeout - (time.monotonic() - started)
                if remaining <= 0:
                    result["status"] = "timeout"
                    break
                for key, _ in selector.select(min(remaining, 0.1)):
                    chunk = os.read(
                        key.fileobj.fileno(), min(65536, MAX_OUTPUT + 1 - len(output))
                    )
                    if not chunk:
                        selector.unregister(key.fileobj)
                    else:
                        output.extend(chunk)
                if len(output) > MAX_OUTPUT:
                    result["status"] = "output-limit"
                    break
            else:
                remaining = timeout - (time.monotonic() - started)
                process.wait(timeout=max(0.001, remaining))
                result["status"] = "passed" if process.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
    except KeyboardInterrupt:
        result["status"] = "cancelled"
    except OSError as exc:
        result["reason"] = f"execution unavailable: {exc.strerror}"
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            process.stdout.close()
            result["exit_code"] = process.returncode
    result.update(
        output_sha256=hashlib.sha256(output).hexdigest(),
        output_bytes=len(output),
        elapsed_seconds=round(time.monotonic() - started, 3),
    )
    tail = output[-4096:].decode("utf-8", errors="replace")
    if result["status"] == "failed" and "ENVIRONMENT_BLOCKED:" in tail:
        result["status"] = "blocked"
    return result | {"output_tail": tail}
