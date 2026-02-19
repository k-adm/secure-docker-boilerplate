# Alpine-based — minimal footprint (~40 MB)
FROM nginx:1.27-alpine

# Upgrade all OS packages to pick up security patches without waiting
# for an upstream base image update (fixes libcrypto3, libssl3, libxml2, libpng)
RUN apk upgrade --no-cache \
    && rm /etc/nginx/conf.d/default.conf

# Copy hardened config and security headers
COPY nginx.conf            /etc/nginx/nginx.conf
COPY security_headers.conf /etc/nginx/security_headers.conf

# Prepare writable dirs for non-root execution
RUN chown -R nginx:nginx /var/cache/nginx /var/run /tmp

# Non-root: listen on unprivileged port, run as nginx user
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=5s \
  CMD wget -qO- http://127.0.0.1:8080/health || exit 1

USER nginx
