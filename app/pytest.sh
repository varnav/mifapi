#!/bin/bash
set -ex

if [ $(grep -c avx2 /proc/cpuinfo) = 0 ]
  then echo "AVX2 support required"
  exit
fi

python -m pytest /app
