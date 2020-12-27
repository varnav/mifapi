# mifapi: Modern Image Formats (JPEG XL and AVIF) API

File transcoding happens in RAM only, files are not saved, and deleted after some time (300 seconds by default).

## Live demo

https://jxl.photos

https://avif.photos

## Run app quickly

You will need `cjxl`, `djxl`, `avifenc` in PATH. You can get it by running `build_cjxl.sh` and `build_avif.sh` as root.

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

## See also

* [makejxl](https://github.com/varnav/makejxl/)
* [makeavif](https://github.com/varnav/makeavif/)
* [filmcompress](https://github.com/varnav/filmcompress/)

