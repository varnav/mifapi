# mifapi: Modern Image Formats (JPEG XL and AVIF) API

## Run app

You will need `cjxl`, `djxl`, `avifenc` in PATH. You can get it by running `build_cjxl.sh` and `build_avif.sh` as root.

```sh
poetry install
cd app
uvicorn main:app --reload
```

Open `http://localhost:8000/docs`

## Live demo

https://jxl.photos

https://avif.photos

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

