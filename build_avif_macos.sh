brew install cmake

brew install ninja

brew install nasm

brew install libpng

brew install jpeg

git clone --depth 1 https://github.com/AOMediaCodec/libavif.git

cd libavif/ext/

./aom.cmd

cd ..

mkdir build

cd build

cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DAVIF_CODEC_AOM=ON -DAVIF_LOCAL_AOM=ON -DAVIF_BUILD_APPS=ON ..

ninja