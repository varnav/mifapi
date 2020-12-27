#!/bin/bash
set -ex

if [ `cat /proc/cpuinfo | grep avx2 | wc -l` -e 0 ]
  then echo "AVX2 support required"
  exit
fi

nginx -t
nginx
python -m pytest /app