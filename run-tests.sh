#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

# Ignoring false positive 36759 (reporting invenio-admin v1.0.1). This can be
# removed when https://github.com/pyupio/safety-db/pull/2274 is merged and
# released.
pipenv check --ignore 36759 --ignore 36810 && \
pipenv run pydocstyle sonar tests docs && \
pipenv run isort -rc -c -df --multi-line=3 --trailing-comma --force-grid-wrap=0 --use-parentheses --line-width=79 && \
pipenv run check-manifest --ignore ".travis-*,docs/_build*" && \
pipenv run sphinx-build -qnNW docs docs/_build/html && \
pipenv run test
