#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

python3 $SCRIPT_DIR/src/fetchPages.py --rootOutputFolder "out" \
--urls \
'your_url1' \
'your_url2' 