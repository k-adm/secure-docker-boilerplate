# Secure Docker Boilerplate for Python Developers

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker Compose](https://img.shields.io/badge/Docker_Compose-v2-blue.svg)](https://docs.docker.com/compose/)
[![Python](https://img.shields.io/badge/Python-3.12-yellow.svg)](https://www.python.org/)

> **95% of Docker tutorials run containers as root. This is dangerous. Here is how to do it right.**

A production-ready, security-hardened Docker boilerplate with **Nginx + FastAPI + PostgreSQL**. Clone it, run it, ship it - with confidence that your containers are locked down from day one.

---

## Security Features

| Feature | What it does |
|---------|-------------|
| Non-root execution | All containers run as unprivileged users |
| Read-only filesystems | App and Nginx have immutable root FS |
| Capabilities dropped | `cap_drop: ALL` - only required caps are added back |
| No privilege escalation | `no-new-privileges` blocks suid/sgid exploits |
| Security headers | CSP, HSTS, X-Frame-Options, X-Content-Type-Options |
| Hidden server version | `server_tokens off` - Nginx version not exposed |
| Isolated network | Services communicate over a private bridge network |
| Healthchecks | Every service has a health probe configured |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/secure-docker-boilerplate.git
cd secure-docker-boilerplate

# 2. Create your .env file
cp .env.example .env

# 3. Build and run
make up
```

Open [http://localhost](http://localhost) - you should see a JSON response from the API.

---

## Architecture

```
                    ┌──────────────┐
                    │   Client     │
                    └──────┬───────┘
                           │ :80
                    ┌──────▼───────┐
                    │    Nginx     │  Reverse proxy
                    │  (Alpine)    │  Security headers
                    └──────┬───────┘
                           │ :8000
                    ┌──────▼───────┐
                    │   FastAPI    │  Application
                    │  (non-root)  │  Read-only FS
                    └──────┬───────┘
                           │ :5432
                    ┌──────▼───────┐
                    │  PostgreSQL  │  Database
                    │  (Alpine)    │  Persistent volume
                    └──────────────┘
```

All services run on an isolated bridge network. Only Nginx exposes port 80 to the host.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info and version |
| `GET` | `/health` | Lightweight healthcheck |
| `GET` | `/db/health` | End-to-end database connectivity check |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |

---

## Available Make Commands

```
make up          Build and start all services
make down        Stop all services
make restart     Rebuild and restart
make logs        Follow logs from all services
make ps          Show running containers
make clean       Stop and remove volumes (full reset)
make health      Check /health and /db/health endpoints
make shell-app   Shell into the app container
make shell-db    Open psql in the database container
```

---

## Project Structure

```
secure-docker-boilerplate/
├── app/
│   ├── Dockerfile            # Multi-stage build, non-root user
│   ├── main.py               # FastAPI app with health endpoints
│   └── requirements.txt      # Pinned dependencies
├── nginx/
│   ├── Dockerfile            # Alpine-based Nginx
│   ├── nginx.conf            # Hardened reverse proxy config
│   └── security_headers.conf # CSP, HSTS, X-Frame-Options, etc.
├── postgres/
│   └── init-scripts/
│       └── 01-init.sql       # Runs on first start (seed data)
├── .dockerignore             # Keep build context clean
├── .env.example              # Template for environment variables
├── .gitignore                # Secrets and cache excluded
├── docker-compose.yml        # Orchestration with security hardening
├── LICENSE                   # MIT
├── Makefile                  # Convenient shortcuts
└── README.md
```

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

[MIT](LICENSE) - use it however you want.
