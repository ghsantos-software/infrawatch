from textwrap import dedent

import pytest

from infrawatch.config import ConfigError, load_config


def _write(tmp_path, content: str) -> str:
    f = tmp_path / "checks.yaml"
    f.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return str(f)


def test_carrega_config_valida(tmp_path):
    path = _write(tmp_path, """
        targets:
          - name: site
            type: http
            url: https://x.com
    """)
    targets = load_config(path)
    assert len(targets) == 1
    assert targets[0]["type"] == "http"


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(ConfigError, match="não encontrado"):
        load_config(str(tmp_path / "nao-existe.yaml"))


def test_sem_chave_targets(tmp_path):
    path = _write(tmp_path, "outra_coisa: 1")
    with pytest.raises(ConfigError, match="targets"):
        load_config(path)


def test_target_sem_campo_obrigatorio(tmp_path):
    path = _write(tmp_path, """
        targets:
          - name: site
            type: http
    """)
    with pytest.raises(ConfigError, match="exige"):
        load_config(path)


def test_type_invalido(tmp_path):
    path = _write(tmp_path, """
        targets:
          - name: x
            type: pombo-correio
            host: x
    """)
    with pytest.raises(ConfigError, match="inválido"):
        load_config(path)