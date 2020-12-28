#!/bin/bash
set -ex

if [ $(grep -c avx2 /proc/cpuinfo) = 0 ]; then
  echo "AVX2 support required"
  exit
fi

nginx -t
nginx
tailon --bind 127.0.0.1:18080 -r '/tailon/' -f /var/log/nginx/* &
python -m pytest /app