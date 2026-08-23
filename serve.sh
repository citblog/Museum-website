#!/bin/sh
cd "$(dirname "$0")"
exec python3 -m http.server 8899 --bind 0.0.0.0
