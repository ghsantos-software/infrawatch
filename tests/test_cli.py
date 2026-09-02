from typer.testing import CliRunner

from infrawatch.checks import CheckResult
from infrawatch.cli import app

runner = CliRunner()

CONFIG_OK = "targets:\n  - name: x\n    type: dns\n    host: x\n"


def _fake_run(saudavel: bool):
    def _run(targets):
        return [CheckResult("alvo", ok=saudavel, detail="x", duration_ms=1.0)]
    return _run


def test_exit_0_quando_tudo_saudavel(tmp_path, monkeypatch):
    cfg = tmp_path / "c.yaml"
    cfg.write_text(CONFIG_OK, encoding="utf-8")
    monkeypatch.setattr("infrawatch.cli.run_checks", _fake_run(True))
    assert runner.invoke(app, ["--config", str(cfg)]).exit_code == 0


def test_exit_1_quando_degradado(tmp_path, monkeypatch):
    cfg = tmp_path / "c.yaml"
    cfg.write_text(CONFIG_OK, encoding="utf-8")
    monkeypatch.setattr("infrawatch.cli.run_checks", _fake_run(False))
    assert runner.invoke(app, ["--config", str(cfg)]).exit_code == 1


def test_exit_2_quando_config_ruim():
    assert runner.invoke(app, ["--config", "nao-existe.yaml"]).exit_code == 2