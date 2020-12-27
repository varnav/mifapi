#!/bin/bash
set -ex
nginx -t
nginx
python -m pytest /app