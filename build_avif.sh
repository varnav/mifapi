#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ $(grep -c avx2 /proc/cpuinfo) == 0 ]
  then echo "AVX2 support required"
  exit
fi

set -ex

DEBIAN_FRONTEND=noninteractive

export MAKEFLAGS=-j$(nproc --ignore=2)
export RUSTFLAGS="-C target-feature=+avx2,+fma"
export CFLAGS="-mavx2 -mfma -ftree-vectorize -pipe"
export CXXFLAGS="${CFLAGS}"

apt-get update
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y
apt-get install -y cmake nasm ninja-build python3-pip libpthread-stubs0-dev
python -m pip install --upgrade pip
python -m pip install setuptools
python -m pip install meson

cd /tmp
rm -rf /tmp/libavif

git clone https://github.com/AOMediaCodec/libavif.git
cd libavif/ext
bash aom.cmd

#bash svt.cmd

export PATH="/root/.cargo/bin:$PATH"
bash rav1e.cmd

bash libjpeg.cmd
bash libyuv.cmd

cd ..
mkdir build
cd build
#cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DAVIF_CODEC_AOM=ON -DAVIF_LOCAL_AOM=ON -DAVIF_CODEC_DAV1D=OFF -DAVIF_LOCAL_DAV1D=OFF -DAVIF_CODEC_RAV1E=ON -DAVIF_LOCAL_RAV1E=ON -DAVIF_CODEC_LIBGAV1=OFF -DAVIF_LOCAL_LIBGAV1=OFF -DAVIF_CODEC_SVT=ON -DAVIF_LOCAL_SVT=ON -DAVIF_LOCAL_LIBYUV=ON -DAVIF_BUILD_EXAMPLES=OFF -DAVIF_BUILD_APPS=ON -DAVIF_BUILD_TESTS=OFF ..
# No rav1e, no svt:
# cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DAVIF_CODEC_AOM=ON -DAVIF_LOCAL_AOM=ON -DAVIF_CODEC_DAV1D=OFF -DAVIF_LOCAL_DAV1D=OFF -DAVIF_CODEC_RAV1E=OFF -DAVIF_LOCAL_RAV1E=OFF -DAVIF_CODEC_LIBGAV1=OFF -DAVIF_LOCAL_LIBGAV1=OFF -DAVIF_CODEC_SVT=OFF -DAVIF_LOCAL_SVT=OFF -DAVIF_LOCAL_LIBYUV=ON -DAVIF_BUILD_EXAMPLES=OFF -DAVIF_BUILD_APPS=ON -DAVIF_BUILD_TESTS=OFF ..
# No svt:
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DAVIF_CODEC_AOM=ON -DAVIF_LOCAL_AOM=ON -DAVIF_CODEC_DAV1D=OFF -DAVIF_LOCAL_DAV1D=OFF -DAVIF_CODEC_RAV1E=ON -DAVIF_LOCAL_RAV1E=ON -DAVIF_CODEC_LIBGAV1=OFF -DAVIF_LOCAL_LIBGAV1=OFF -DAVIF_CODEC_SVT=OFF -DAVIF_LOCAL_SVT=OFF -DAVIF_LOCAL_LIBYUV=ON -DAVIF_BUILD_EXAMPLES=OFF -DAVIF_BUILD_APPS=ON -DAVIF_BUILD_TESTS=OFF ..
ninja

cp /tmp/libavif/build/avifenc /usr/bin/
rm -rf /tmp/cavif