# Copyright © 2022 Intel Corporation
#
# SPDX-License-Identifier: Apache License 2.0
ARG NGINX_VERSION


FROM nginx:${NGINX_VERSION}

RUN set -ex \
  ; apt-get update -yqq >/dev/null \
  ; apt-get upgrade -yqq >/dev/null \
  ; rm -rf /var/lib/apt/lists/* \
  ; :

COPY nginx/ /etc/nginx/

RUN mkdir -p /var/run/nginx

ENTRYPOINT []

CMD ["nginx", "-g", "daemon off;"]
