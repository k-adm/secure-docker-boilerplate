# Security Audit: Trivy Scan - 2026-02-19

**Tool:** Trivy v0.69.1 · **Scanners:** vuln, misconfig, secret · **Filter:** HIGH, CRITICAL

## Scope

Three container images that make up the stack:

| Image | OS | Role |
|-------|----|------|
| `secure-docker-boilerplate-nginx:latest` | Alpine Linux 3.21.3 | Reverse proxy (port 80) |
| `secure-docker-boilerplate-app:latest` | Debian 13.3 (Trixie) | FastAPI application (port 8000, internal) |
| `postgres:16-alpine` | Alpine Linux 3.23.3 | PostgreSQL database (port 5432, internal) |

---

## Results Summary

| Image | CRITICAL | HIGH | Misconfigs | Secrets | Exploitable | Status |
|-------|----------|------|-----------|---------|-------------|--------|
| nginx | 4 | 13 | 0 ✅ | 0 ✅ | **0** | Fixed - `apk upgrade` added |
| app | 0 | 3 | 0 ✅ | 0 ✅ | **1** | Fixed - FastAPI bumped + nginx mitigation |
| postgres | 1 | 5 | 0 ✅ | 0 ✅ | **0** | No action needed |

The "Exploitable" column reflects actual attack reachability in this specific deployment context, not the raw CVSS score.

---

## Key Findings

### nginx - 17 CVEs in OS libraries (0 exploitable)

All findings are in Alpine OS libraries bundled with the `nginx:1.27-alpine` base image. **None are reachable through HTTP reverse-proxy traffic.**

| Package | Installed | Fixed | CVEs |
|---------|-----------|-------|------|
| `libcrypto3` / `libssl3` | 3.3.3-r0 | 3.3.6-r0 | CVE-2025-15467 (CVSS 9.8), CVE-2025-69419, CVE-2025-69421 |
| `libxml2` | 2.13.4-r5 | 2.13.9-r0 | CVE-2025-49794 (CVSS 9.1), CVE-2025-49796 (CVSS 9.1), CVE-2025-49795, CVE-2025-6021, CVE-2025-32414, CVE-2025-32415 |
| `libpng` | 1.6.47-r0 | 1.6.54-r0 | CVE-2025-64720, CVE-2025-65018, CVE-2025-66293, CVE-2026-22695, CVE-2026-22801 |

**Why not exploitable:** OpenSSL CVEs require CMS/PKCS#12 input that Nginx never processes in proxy mode; libxml2 CVEs require attacker-controlled XML; libpng is not involved in client request handling. Nginx 1.27.5 itself has zero CVEs.

### app - 3 CVEs, 1 exploitable

**CVE-2025-62727** (starlette 0.41.3, CVSS 7.5) - **the only actionable finding across all three images.**

An unauthenticated attacker can send a crafted `Range` header that triggers quadratic-time processing in Starlette's `FileResponse` range-merging logic → CPU exhaustion / DoS. No authentication required, one request is enough.

Current endpoints (`/`, `/health`, `/db/health`) don't use `FileResponse` and are not directly vulnerable. The `/docs` Swagger UI endpoint uses Starlette static file serving and represents a potential attack surface.

**CVE-2026-0861** (glibc 2.41, CVSS 8.1) - no patch available for Debian 13.3. Requires attacker control of both `size` (≈ `PTRDIFF_MAX`) and `alignment` ([1<<62+1, 1<<63]) in the same `memalign` call - not achievable through FastAPI/Python. Track at [Debian Security Tracker](https://security-tracker.debian.org/tracker/CVE-2026-0861).

### postgres - 6 CVEs in gosu binary (0 exploitable)

Alpine 3.23.3 OS packages are fully clean. All 6 CVEs are in `/usr/local/bin/gosu` compiled with Go stdlib v1.24.6. `gosu` is a minimal privilege-dropping tool that runs `setuid` + `exec` - it makes **no network connections, parses no archives, and does not use TLS**. All vulnerable code paths are unreachable.

---

## Fixes Applied

### 1. `nginx/Dockerfile` - OS package patching

```dockerfile
# Before
RUN rm /etc/nginx/conf.d/default.conf

# After
RUN apk upgrade --no-cache \
    && rm /etc/nginx/conf.d/default.conf
```

`apk upgrade --no-cache` upgrades all installed packages (libcrypto3, libssl3, libxml2, libpng) to patched versions on every build, without waiting for a new upstream base image. Combined into a single `RUN` layer to avoid adding image layers.

### 2. `app/requirements.txt` - FastAPI / Starlette upgrade

```diff
-fastapi==0.115.6
+fastapi==0.128.0
```

FastAPI is upgraded to pull in starlette ≥ 0.49.1 (which contains the fix for CVE-2025-62727). Per [FastAPI documentation](https://fastapi.tiangolo.com/deployment/versions/#about-starlette), starlette should not be pinned independently - upgrading FastAPI is the correct approach.

### 3. `nginx/nginx.conf` - Range header stripping (defence-in-depth)

```nginx
# Inside location / block
proxy_set_header Range "";
```

Per Nginx docs, a header set to an empty string is not forwarded to the upstream. This removes the `Range` header before it reaches FastAPI, blocking CVE-2025-62727 independently of the library version.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| `apk upgrade` instead of waiting for a new base image | Patches are already in Alpine repos; waiting for `nginx:1.27-alpine` to rebuild could take days. Combined with the existing `RUN` to keep layer count constant. |
| Upgrade FastAPI, not pin starlette directly | FastAPI documents this explicitly. A separate `starlette>=0.49.1` pin would conflict with FastAPI's own version constraint. |
| Add `proxy_set_header Range ""` in Nginx | Defence-in-depth: protects even if the app is deployed with an older starlette version. Doesn't affect current endpoints (none use `FileResponse`). |
| No action on postgres | `gosu` CVEs have zero attack surface - it's a startup-only tool that never processes external input. Updating requires the upstream image maintainers to rebuild with a patched Go toolchain. |
| No action on glibc CVE-2026-0861 | No fix available for Debian 13.3; real-world exploitability through Python/FastAPI is negligible. |

---

## See Also

- [nginx detailed report](vulnerability-report-nginx-en.md)
- [app detailed report](vulnerability-report-app-en.md)
- [postgres detailed report](vulnerability-report-db-en.md)
