# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

# Self signed certificate generated at build time, so that no private key is
# versioned. Built in a separate stage because the haproxy image ships no
# openssl command. In production the external certificate is provided by the
# deployment, through Let's Encrypt.
FROM alpine:3 AS certificate
RUN apk add --no-cache openssl \
    && openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
       -keyout /cert.key -out /cert.crt \
       -subj "/CN=localhost" \
       -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" \
    && cat /cert.crt /cert.key > /cert.pem

FROM haproxy:1.8
RUN mkdir -p /usr/local/var/lib/haproxy/
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
# HAProxy expects the certificate and its key concatenated in a single file.
COPY --from=certificate /cert.pem /usr/local/etc/cert.pem
