import json

from infrawatch.checks import CheckResult
from infrawatch.report import to_json, to_markdown

RESULTS = [
    CheckResult("A", ok=True, detail="tudo certo", duration_ms=10.0),
    CheckResult("B", ok=False, detail="caiu", duration_ms=20.0),
]
NOW = "2026-01-01T00:00:00+00:00"


def test_markdown_tem_resumo_e_linhas():
    md = to_markdown(RESULTS, NOW)
    assert "1 de 2 saudáveis" in md
    assert "| ✅ | A |" in md
    assert "| ❌ | B |" in md
    assert NOW in md


def test_json_estrutura():
    data = json.loads(to_json(RESULTS, NOW))
    assert data["generated_at"] == NOW
    assert data["summary"] == {"total": 2, "healthy": 1, "degraded": 1}
    assert data["results"][0]["name"] == "A"