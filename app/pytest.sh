#!/bin/bash
set -ex

if [ `cat /proc/cpuinfo | grep avx2 | wc -l` -eq 0 ]
  then echo "AVX2 support required"
  exit
fi

python -m pytest /app
