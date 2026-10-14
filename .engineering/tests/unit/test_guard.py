"""The unit tier refuses subprocesses, naming the test and the command."""

import os
import subprocess

import pytest


def test_starting_a_subprocess_fails_the_unit_test(request):
    with pytest.raises(pytest.fail.Exception) as failure:
        subprocess.run(["git", "status"], check=False)
    message = str(failure.value)
    assert message.startswith(f"{request.node.nodeid} started a subprocess:")
    assert "['git', 'status']" in message


def test_shell_commands_are_refused_too(request):
    with pytest.raises(pytest.fail.Exception) as failure:
        os.system("make check")
    assert str(failure.value).startswith(
        f"{request.node.nodeid} started a subprocess: 'make check'"
    )
