"""O motor: para cada alvo, chama a verificação certa, mede o tempo e junta tudo."""

import time

from infrawatch.checks import (
    CheckResult,
    check_dns,
    check_http,
    check_tcp,
    check_tls,
)

# Tabela de despacho: liga o "type" do YAML à função que faz a verificação.
# Adicionar um check novo = UMA linha aqui. Sem if/elif.
CHECKS = {
    "http": check_http,
    "tcp": check_tcp,
    "tls": check_tls,
    "dns": check_dns,
}


def run_checks(targets: list[dict]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for target in targets:
        func = CHECKS[target["type"]]  # o config.py já garantiu que o type é válido
        start = time.perf_counter()
        try:
            result = func(target)
        except Exception as exc:
            # rede de segurança: se um check tiver um bug não previsto,
            # registramos como falha e seguimos — não derrubamos a run inteira.
            result = CheckResult(
                name=target["name"],
                ok=False,
                detail=f"erro inesperado: {exc.__class__.__name__}",
            )
        result.duration_ms = round((time.perf_counter() - start) * 1000, 1)
        results.append(result)
    return results