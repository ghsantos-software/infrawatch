"""Transforma a lista de CheckResult em texto: Markdown (humano) e JSON (máquina)."""

import json
from dataclasses import asdict

from infrawatch.checks import CheckResult


def _summary(results: list[CheckResult]) -> dict:
    total = len(results)
    healthy = sum(1 for r in results if r.ok)
    return {"total": total, "healthy": healthy, "degraded": total - healthy}


def to_markdown(results: list[CheckResult], generated_at: str) -> str:
    s = _summary(results)
    linhas = [
        "# Relatório de saúde da infraestrutura",
        "",
        f"Gerado em: `{generated_at}`",
        "",
        f"**{s['healthy']} de {s['total']} saudáveis** · {s['degraded']} com problema",
        "",
        "| Status | Alvo | Detalhe | Tempo |",
        "|---|---|---|---|",
    ]
    for r in results:
        icone = "✅" if r.ok else "❌"
        # escapa "|" pra não quebrar a coluna da tabela
        nome = r.name.replace("|", "\\|")
        detalhe = r.detail.replace("|", "\\|")
        linhas.append(f"| {icone} | {nome} | {detalhe} | {r.duration_ms} ms |")
    return "\n".join(linhas) + "\n"


def to_json(results: list[CheckResult], generated_at: str) -> str:
    payload = {
        "generated_at": generated_at,
        "summary": _summary(results),
        "results": [asdict(r) for r in results],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"