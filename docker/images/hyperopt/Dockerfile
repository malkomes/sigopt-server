# Copyright © 2022 Intel Corporation
#
# SPDX-License-Identifier: Apache License 2.0
ARG PYTHON_MAJOR
ARG PYTHON_MINOR


FROM python:${PYTHON_MAJOR}.${PYTHON_MINOR}-buster

ENV PYTHONPATH=/sigopt-python
RUN set -ex \
  ; apt-get update \
  ; apt-get -y install --no-install-recommends \
      default-jre=2:1.11-* \
      git=1:2.20.* \
  ; rm -rf /var/lib/apt/lists/* \
  ; :
RUN mkdir /hyperopt-test
WORKDIR /hyerpopt-test
COPY docker/images/hyperopt/start-worker.sh /hyerpopt-test
