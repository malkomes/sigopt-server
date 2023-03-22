#!/usr/bin/env bash
set -e
set -o pipefail

./tools/protobuf/compile.sh

./test/unit_tests
./pp py.test -rw sigoptcompute/testcompute/ --durations 5