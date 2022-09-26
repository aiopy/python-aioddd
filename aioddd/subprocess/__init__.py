from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import create_subprocess_exec, create_subprocess_shell, sleep, wait_for
from typing import Any, Dict, NamedTuple, Optional

_flag_subprocess_running: Dict[str, bool] = {}

DEFAULT_WAIT_FLAG_SLEEP: float = 0.1


async def _wait_flagged_subprocess_running(wait_flag: str) -> None:
    if not _flag_subprocess_running[wait_flag]:
        return
    await sleep(DEFAULT_WAIT_FLAG_SLEEP)


class SubprocessResult(NamedTuple):
    return_code: int
    stdout: Optional[str] = None
    stderr: Optional[str] = None


def _create_subprocess(  # type: ignore
    *args: Any,
    shell: bool,
    stdout: Optional[int],
    stderr: Optional[int],
    limit: int,
    **kwds: Any,
):
    return (
        create_subprocess_shell(*args, stdout=stdout, stderr=stderr, limit=limit, **kwds)  # type: ignore
        if shell
        else create_subprocess_exec(*args, stdout=stdout, stderr=stderr, limit=limit, **kwds)
    )


async def run_subprocess(
    *args: str,
    shell: bool = False,
    encoding: str = 'utf8',
    timeout: Optional[float] = None,
    wait_flag: Optional[str] = None,
    wait_flag_timeout: Optional[float] = None,
    stdout: Optional[int] = -1,  # see asyncio.subprocess.PIPE,
    stderr: Optional[int] = -1,  # see asyncio.subprocess.PIPE,
    limit: int = 2**64,  # see streams._DEFAULT_LIMIT
    **kwds: Dict[str, Any],
) -> SubprocessResult:
    """
    Creates and runs a subprocess with or without shell.

    Provides to time out the Python managed subprocess using asyncio.wait_for.
    Provides to flag Python managed subprocess with timeout as well using unique keys and asyncio.wait_for.

    stdin not supported!

    When shell=True *args will be the "cmd" arg for asyncio.subprocess.create_subprocess_shell
    When shell=False *args will be the "*args" arg (not "program" arg) for asyncio.subprocess.create_subprocess_exec

    Return (return_code, stdout, stderr)
    """
    _ = [kwds.pop(key, None) for key in ['shell', 'encoding', 'timeout', 'wait_flag', 'wait_flag_timeout']]
    if wait_flag:
        if wait_flag not in _flag_subprocess_running:
            _flag_subprocess_running[wait_flag] = True
        elif _flag_subprocess_running.get(wait_flag, True):
            await wait_for(fut=_wait_flagged_subprocess_running(wait_flag=wait_flag), timeout=wait_flag_timeout)
            _flag_subprocess_running[wait_flag] = True
    proc = await _create_subprocess(
        *args,
        shell=shell,  # nosec
        stdout=stdout,
        stderr=stderr,
        limit=limit,
        **kwds,
    )

    try:
        return_code = await wait_for(fut=proc.wait(), timeout=timeout)
    except AsyncTimeoutError:
        proc.terminate()
        return_code = await proc.wait()
    finally:
        if wait_flag and wait_flag in _flag_subprocess_running:
            del _flag_subprocess_running[wait_flag]

    stdout_: Optional[bytes] = await proc.stdout.read()
    stderr_: Optional[bytes] = await proc.stderr.read()

    return SubprocessResult(
        return_code=return_code,
        stdout=stdout_.strip().decode(encoding) if stdout_ else None,
        stderr=stderr_.strip().decode(encoding) if stderr_ else None,
    )
