#!/bin/bash

set -eu


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_NAME=`basename "$0"`


GEN_PATH="$SCRIPT_DIR/../src/generator.py"


## execute

$GEN_PATH --input_config "$SCRIPT_DIR/protocol.csv" --output_dir "$SCRIPT_DIR/output" $@

