#!/bin/bash

set -e

PYTHON_EXEC="/venv/bin/python"

usage() {
    echo "Usage: $0 <mode> [refresh_token]"
    echo "  mode: app | workloadidentity | refreshtoken"
    echo "  refresh_token: required only for 'refreshtoken' mode"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

MODE="$1"
shift

case "$MODE" in
    app)
        exec "$PYTHON_EXEC" entra_app_password.py
        ;;
    workloadidentity)
        exec "$PYTHON_EXEC" entra_workload_identity_password.py
        ;;
    refreshtoken)
        if [ $# -lt 1 ]; then
            echo "Error: refresh_token argument required for 'refreshtoken' mode."
            usage
        fi
        REFRESH_TOKEN="$1"
        exec "$PYTHON_EXEC" entra_refresh_token_password.py "$REFRESH_TOKEN"
        ;;
    *)
        echo "Error: Unknown mode '$MODE'"
        usage
        ;;
esac