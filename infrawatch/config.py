"""Carrega e valida o arquivo de configuração (checks.yaml)."""

from pathlib import Path # ler o arquivo de configuração

import yaml

# Para cada tipo de check, os campos obrigatórios ALÉM de "name" e "type".
REQUIRED_FIELDS: dict[str, list[str]] = {
    "http": ["url"],
    "tcp": ["host", "port"],
    "tls": ["host"],
    "dns": ["host"],
}


class ConfigError(Exception):
    """Erro no arquivo de configuração. A mensagem já é amigável para o usuário."""


def load_config(path: str) -> list[dict]:
    """Lê o YAML, valida e devolve a lista de alvos."""
    file = Path(path)
    if not file.is_file():
        raise ConfigError(f"arquivo não encontrado: {path}")

    # safe_load interpreta só tipos básicos (dict, list, str, int...).
    # yaml.load (sem "safe_") pode executar código arbitrário — nunca use.
    data = yaml.safe_load(file.read_text(encoding="utf-8"))

    if not isinstance(data, dict) or "targets" not in data:
        raise ConfigError("o arquivo precisa ter uma chave 'targets' no topo")

    targets = data["targets"]
    if not isinstance(targets, list) or not targets:
        raise ConfigError("'targets' precisa ser uma lista com pelo menos um item")

    for i, target in enumerate(targets, start=1):
        _validate_target(i, target)

    return targets


def _validate_target(index: int, target: object) -> None:
    """Valida um único alvo; erro aponta a posição e o nome."""
    where = f"target #{index}"

    if not isinstance(target, dict):
        raise ConfigError(f"{where}: cada alvo precisa ser um bloco com campos (name, type, ...)")

    if "name" not in target:
        raise ConfigError(f"{where}: falta o campo 'name'")

    check_type = target.get("type")
    if check_type not in REQUIRED_FIELDS:
        conhecidos = ", ".join(sorted(REQUIRED_FIELDS))
        raise ConfigError(
            f"{where} ('{target['name']}'): type '{check_type}' inválido — use: {conhecidos}"
        )

    faltando = [campo for campo in REQUIRED_FIELDS[check_type] if campo not in target]
    if faltando:
        raise ConfigError(
            f"{where} ('{target['name']}'): type '{check_type}' exige o(s) campo(s) {faltando}"
        )