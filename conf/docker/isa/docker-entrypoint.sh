#!/bin/sh
# vim:sw=4:ts=4:et

set -e

if [ "$1" = "apiserver" ]; then
    if [ -e /usr/local/isa/api/main.py ]; then
        cd /usr/local/isa/api
        python -m uvicorn main:app --reload --port 80 --host 0.0.0.0
    else
        echo "FastAPI entrypoint not find."
    fi
else
    exec "$@"
fi
