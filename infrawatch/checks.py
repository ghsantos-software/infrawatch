"""As verificações. Cada função recebe um alvo (dict) e devolve um CheckResult.

Regra de ouro: um check NUNCA levanta exceção — captura o erro e devolve ok=False.
"""

import socket
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

# Todo check tem no máximo isso pra responder. SEM timeout, um host travado
# trava a ferramenta pra sempre.
TIMEOUT_SECONDS = 5


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str
    duration_ms: float = 0.0


def check_http(target: dict) -> CheckResult:
    name = target["name"]
    expected = target.get("expect_status", 200)
    try:
        response = httpx.get(target["url"], timeout=TIMEOUT_SECONDS, follow_redirects=True)
    except httpx.RequestError as exc:
        return CheckResult(name, ok=False, detail=f"não respondeu: {exc.__class__.__name__}")
    return CheckResult(
        name,
        ok=response.status_code == expected,
        detail=f"HTTP {response.status_code} (esperado {expected})",
    )


def check_tcp(target: dict) -> CheckResult:
    name = target["name"]
    host, port = target["host"], target["port"]
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT_SECONDS):
            return CheckResult(name, ok=True, detail=f"porta {port} aberta")
    except OSError as exc:
        return CheckResult(name, ok=False, detail=f"porta {port} fechada: {exc.__class__.__name__}")


def check_tls(target: dict) -> CheckResult:
    name = target["name"]
    host = target["host"]
    port = target.get("port", 443)
    warn_days = target.get("warn_days", 30)
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=TIMEOUT_SECONDS) as sock:
            with context.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
    except (OSError, ssl.SSLError) as exc:
        return CheckResult(name, ok=False, detail=f"falha no TLS: {exc.__class__.__name__}")

    expires = datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notAfter"]), tz=timezone.utc)
    days_left = (expires - datetime.now(timezone.utc)).days
    return CheckResult(
        name,
        ok=days_left >= warn_days,
        detail=f"expira em {days_left} dias (alerta abaixo de {warn_days})",
    )


def check_dns(target: dict) -> CheckResult:
    name = target["name"]
    try:
        infos = socket.getaddrinfo(target["host"], None)
    except socket.gaierror as exc:
        return CheckResult(name, ok=False, detail=f"não resolveu: {exc.__class__.__name__}")
    ips = sorted({info[4][0] for info in infos})
    return CheckResult(name, ok=True, detail=f"resolveu para {', '.join(ips)}")