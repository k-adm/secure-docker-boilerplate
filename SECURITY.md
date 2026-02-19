# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` (latest) | ✅ |

This is a boilerplate / template repository. Security fixes are applied to the `main` branch only.

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not open a public GitHub Issue**.

Instead:
1. Open a [GitHub Security Advisory](../../security/advisories/new) (private disclosure)
2. Or email the maintainer directly (see profile)

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- Affected component (nginx, app, postgres, configuration)

You can expect an acknowledgement within 48 hours and a fix or mitigation within 7 days for critical issues.

## Security Design

This boilerplate is built with security as a first-class concern:

| Control | Implementation |
|---------|---------------|
| Non-root containers | All services run as unprivileged users |
| Read-only filesystems | App and Nginx have immutable root FS |
| Dropped capabilities | `cap_drop: ALL` — only required caps re-added |
| No privilege escalation | `no-new-privileges` flag set |
| Security headers | CSP, X-Frame-Options, X-Content-Type-Options, HSTS (ready, activate after TLS) |
| Hidden server tokens | `server_tokens off` |
| Isolated network | Services communicate over a private bridge network only |
| Healthchecks | Every service has a health probe configured |

## Security Audits

| Date | Tool | Version | Scope | Report |
|------|------|---------|-------|--------|
| 2026-02-19 | [Trivy](https://github.com/aquasecurity/trivy) | 0.69.1 | All container images (nginx, app, postgres) | [docs/security/](docs/security/trivy-audit-2026-02-19.md) |

### 2026-02-19 Audit — TL;DR

Scanned all three images with `--scanners vuln,misconfig,secret --severity HIGH,CRITICAL`.

- **0 misconfigurations** across all images
- **0 secrets** detected in any image
- **1 exploitable CVE** found and fixed: [CVE-2025-62727](https://nvd.nist.gov/vuln/detail/CVE-2025-62727) (Starlette DoS via Range header) — resolved by upgrading FastAPI and stripping the `Range` header in Nginx
- All other findings (17 in nginx OS libs, 6 in postgres gosu binary) assessed as **not exploitable** in this deployment context

See the [full audit report](docs/security/trivy-audit-2026-02-19.md) for details.
