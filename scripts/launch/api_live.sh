#!/usr/bin/env bash
# Copyright © 2023 Intel Corporation
#
# SPDX-License-Identifier: Apache License 2.0
set -e
set -o pipefail

COMMAND=(./scripts/launch/all_live.sh --no-web --foreground "$@")

exec "${COMMAND[@]}"
