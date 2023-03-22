#!/usr/bin/env bash
set -e
set -o pipefail

./scripts/launch/compose.sh run --rm createdb \
  python -m zigopt.utils.create_database "$@"