[![Docker Pulls](https://img.shields.io/docker/pulls/varnav/mifapi.svg)](https://hub.docker.com/r/varnav/mifapi) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT/)

---
**NOTE**

`avif.photos` webservice is currently down because I don't really want to pay for it, so links are not functional. Please spin up your own copy.

---

# mifapi: Modern Image Formats (JPEG XL and AVIF) Web API Service

* File transcoding happens in RAM only, files are not saved, and deleted after some time (300 seconds by default)
* All components of the app will correctly utilize multiple CPU cores, AVX2 support is mandatory
* Uses latest versions of tools and libraries
* [A+ rated](https://www.ssllabs.com/ssltest/analyze.html?d=avif.photos) SSL configuration with TLS 1.3 and HTTP/2
* Asyncronous converters (optional) will output dowload URL of the file, but actual transcoding will be done few seconds later, and not guaranteed to succeed

JPEG served us well for decades. Time to dethrone it.

## API documentation

* [Swagger](https://jxl.photos/docs)

* [Redoc](https://jxl.photos/redoc)

## Client library

* [pymifapi](https://github.com/varnav/pymifapi/)

## Live demo

* https://jxl.photos

* https://avif.photos

## How to use

### sh

```sh
curl -X POST "https://jxl.photos/api/v1/jxl/encode" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "file=@IMG_20201219_142048.JPG;type=image/jpeg" | python3 -c "import sys, json; print(json.load(sys.stdin)['dl_uri'])" | xargs -n1 curl -O
```

### Python

* [sample_request.py](sample_request.py)

## Run app quickly

You will need [cjxl/djxl](https://gitlab.com/wg1/jpeg-xl), [avifenc](https://github.com/AOMediaCodec/libavif) in PATH. You can get it by running `build_cjxl.sh` and `build_avif.sh` as root.

```sh
poetry install
cd app
uvicorn main:app --reload
```

Open `http://localhost:8000/docs`

## Run app in production

[Dockerfile](Dockerfile) will build necessary tools and run app behind nginx. You may use letsencrypt (default) or your own certs. You need to edit [nginx.conf](nginx.conf) for your own needs. Then you can build docker image and run it this way:

```sh
docker build -t mycoolcompany/mifapi .
docker run -d --name mifapi --restart on-failure:10 --security-opt no-new-privileges --tmpfs /tmp/mifapi_temp -p 80:80 -p 443:443 -v /etc/letsencrypt:/etc/letsencrypt mycoolcompany/mifapi
```

## AVIF

* Royalty free
* Very efficient at low bitrates
* Has some adoption
* Slow (for now)
* May be bad at low bitrates (loss of detail)

## JPEG XL

* Very new
* Allows lossless compression and decompression of JPEGs
* Best for high quality high bitrate images

## TODO

* Optimized defaults
* More parameters to tune conversion

## Known issues

* EXIF preservation is unclear
* SVT and RAV1E encoders support is experimental. Practical usefulness currently is low.

## Other tools

* [makejxl](https://github.com/varnav/makejxl/) - Converter to JPEG XL
* [makeavif](https://github.com/varnav/makeavif/) - Converter to AVIF
* [squoosh CLI](https://github.com/GoogleChromeLabs/squoosh/tree/dev/cli) - Converter/optimizer from Google
* [optimize-images](https://github.com/victordomingos/optimize-images/) - JPEG optimizer
