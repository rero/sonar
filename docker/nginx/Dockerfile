# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

FROM nginx

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
        libxml2 \
        libxml2-dev \
        libxmlsec1 \
        libxmlsec1-dev

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/* /etc/nginx/conf.d/
COPY test.key /etc/ssl/private/test.key
COPY test.crt /etc/ssl/certs/test.crt
