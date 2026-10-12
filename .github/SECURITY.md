# Security Policy

## Supported Versions

PokeWrap is in early development. Only the latest release receives
security updates.

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |
| < 0.1   | ❌        |

## Reporting a Vulnerability

If you believe you have found a security vulnerability in PokeWrap,
please report it **privately** using GitHub Security Advisories:

👉 https://github.com/Alike-Dev/poke-wrap/security/advisories/new

Please include:

- A description of the vulnerability.
- Steps to reproduce, with a minimal code sample if possible.
- The version of `poke-wrap-client` you tested.
- Any potential impact you can foresee.

You can expect an initial response within **7 days**. If the report is
accepted, a fix will be released as soon as practical and you will be
credited in the release notes unless you prefer to remain anonymous.

Please do **not** open public GitHub issues for security problems.

## Scope

PokeWrap is an HTTP client for PokeAPI. It does not process untrusted
input, store secrets, or perform authentication. The most relevant
attack surfaces are:

- Malicious responses from a compromised PokeAPI endpoint.
- SSRF through the hydration layer (mitigated: only URLs starting with
  `https://pokeapi.co/api/v2/` are followed).
- Dependency vulnerabilities in `httpx`, `hishel` or `pydantic`.

Out of scope: bugs in PokeAPI itself, and issues caused by users
monkey-patching library internals.