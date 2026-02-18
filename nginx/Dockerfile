# Alpine-based — minimal footprint (~40 MB)
FROM nginx:1.27-alpine

# Remove default config to avoid conflicts
RUN rm /etc/nginx/conf.d/default.conf

# Copy hardened config and security headers
COPY nginx.conf            /etc/nginx/nginx.conf
COPY security_headers.conf /etc/nginx/security_headers.conf

EXPOSE 80
