# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM nginx

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/* /etc/nginx/conf.d/

# Self signed certificate generated at build time, so that no private key is
# versioned. It is only used for the connection from the load balancer, which
# does not verify it.
RUN openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
    -keyout /etc/ssl/private/test.key -out /etc/ssl/certs/test.crt \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:frontend,IP:127.0.0.1"
