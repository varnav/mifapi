# mifapi: Modern Image Formats (JPEG XL and AVIF) API

## Run app

You will need cjxl in path. You can get it by running build_cjxl.sh as root.

```sh
poetry install
cd app
uvicorn main:app --reload
```

Open `http://localhost:8000/docs`

## Live demo

https://jxl.photos

https://avif.photos