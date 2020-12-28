[![Docker Pulls](https://img.shields.io/docker/pulls/varnav/mifapi.svg)](https://hub.docker.com/r/varnav/mifapi) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT/)

# mifapi: Modern Image Formats (JPEG XL and AVIF) Web API

* File transcoding happens in RAM only, files are not saved, and deleted after some time (300 seconds by default)
* All components of the app will correctly utilize multiple CPU cores
* Mandatory AVX2 support improves performance
* Asyncronous converters (optional) will output dowload URL of the file, but actual transcoding will be done few seconds later, and not guaranteed to succeed
* JPEG served us well for decades. Time to dethrone it.

## Live demo

https://jxl.photos  
https://avif.photos

## How to use

### sh

```sh
curl -X POST "https://jxl.photos/api/v1/jxl/encode" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "file=@IMG_20201219_142048.JPG;type=image/jpeg" | python3 -c "import sys, json; print(json.load(sys.stdin)['dl_uri'])" | xargs -n1 curl -O
```

## Run app quickly

You will need [cjxl/djxl](https://gitlab.com/wg1/jpeg-xl), [avifenc](https://github.com/AOMediaCodec/libavif) in PATH. You can get it by running `build_cjxl.sh` and `build_avif.sh` as root.

```sh
poetry install
cd app
uvicorn main:app --reload
```

Open `http://localhost:8000/docs`

## Run app in production

[Dockerfile](Dockerfile) will build necessary tools and run app behind nginx with SSL 1.3 and http/2 support. You may use letsencrypt (default) or your own certs. You need to edit [nginx.conf](nginx.conf) for your own needs. Then you can build docker image and run it this way:

```sh
docker build -t mycoolcompany/mifapi .
docker run -d --name mifapi --restart on-failure:10 --security-opt no-new-privileges --tmpfs /tmp/mifapi_temp -p 80:80 -p 443:443 -v /etc/letsencrypt:/etc/letsencrypt mycoolcompany/mifapi
```

## AVIF

* Royalty free
* Very efficient
* Has some adoption
* Slow (for now)

## JPEG XL

* Very new
* Allows lossless compression and decompression of JPEGs

## TODO

* Optimized defaults
* More parameters to tune conversion

## Known issues

* EXIF preservation is unclear

## See also

* [makejxl](https://github.com/varnav/makejxl/)
* [makeavif](https://github.com/varnav/makeavif/)
* [filmcompress](https://github.com/varnav/filmcompress/)
* [optimize-images](https://github.com/victordomingos/optimize-images/)
