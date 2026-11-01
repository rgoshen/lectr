import pytest

from lectr import __version__
from lectr.cli import main


def test_version_flag_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"lectr {__version__}"


def test_main_without_arguments_returns_zero() -> None:
    assert main([]) == 0
