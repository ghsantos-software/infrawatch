"""Interface de linha de comando.  Rode:  python -m infrawatch --help"""

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

import typer

from infrawatch.config import ConfigError, load_config
from infrawatch.report import to_json, to_markdown
from infrawatch.runner import run_checks

app = typer.Typer(
    add_completion=False,
    help="Verifica a saúde de uma infraestrutura e gera um relatório.",
)


class Format(str, Enum):
    markdown = "markdown"
    json = "json"


@app.command()
def main(
    config: Path = typer.Option("checks.yaml", "--config", "-c", help="YAML com os alvos."),
    out: Path | None = typer.Option(None, "--out", "-o", help="Arquivo de saída (padrão: tela)."),
    fmt: Format = typer.Option(Format.markdown, "--format", "-f", help="Formato do relatório."),
) -> None:
    # 1. Carregar e validar a config. Config quebrada -> exit 2.
    try:
        targets = load_config(str(config))
    except ConfigError as exc:
        typer.secho(f"erro de configuração: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    # 2. Rodar os checks.
    results = run_checks(targets)

    # 3. Montar o relatório (a mesma hora vai pros dois formatos).
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    render = to_json if fmt is Format.json else to_markdown
    report = render(results, generated_at)

    # 4. Gravar no arquivo OU jogar no stdout.
    if out is not None:
        out.write_text(report, encoding="utf-8")
        typer.secho(f"relatório salvo em {out}", fg=typer.colors.CYAN, err=True)
    else:
        typer.echo(report)

    # 5. Resumo no stderr (não suja o stdout / o arquivo) + exit code.
    degraded = [r for r in results if not r.ok]
    if degraded:
        nomes = ", ".join(r.name for r in degraded)
        typer.secho(
            f"{len(degraded)}/{len(results)} com problema: {nomes}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    typer.secho(f"tudo saudável ({len(results)} checks)", fg=typer.colors.GREEN, err=True)