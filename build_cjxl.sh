#!/bin/bash -ex

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ $(grep -c avx2 /proc/cpuinfo) == 0 ]
  then echo "AVX2 support required"
  exit
fi
set -ex

export MAKEFLAGS=-j$(nproc --ignore=2)
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get -y install python3-pip git wget ca-certificates cmake pkg-config libbrotli-dev libgif-dev libjpeg-dev libopenexr-dev libpng-dev libwebp-dev clang-7
export CC=clang-7 CXX=clang++-7

cd /tmp/
rm -rf jpeg-xl
git clone https://gitlab.com/wg1/jpeg-xl.git --recursive
cd jpeg-xl
rm -rf build
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF ..
cmake --build . -- -j$(nproc)
