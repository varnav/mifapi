FROM python:3 as builder

COPY ./build_cjxl.sh .
RUN /bin/bash ./build_cjxl.sh

COPY ./build_avif.sh .
RUN /bin/bash ./build_avif.sh

# Docs https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV PORT=8000
ENV DEBIAN_FRONTEND=noninteractive

COPY --from=builder /tmp/jpeg-xl/build/tools/djxl /tmp/jpeg-xl/build/tools/cjxl /tmp/libavif/build/avifenc /usr/bin/

COPY ./pyproject.toml .
COPY ./html /html/

RUN set -ex && \
    python -m pip install -U pip && \
    python -m pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev && \
    apt-get update && apt-get install --no-install-recommends -y libgif-dev nginx software-properties-common ca-certificates && \
    mkdir /tmp/mifapi_temp && \
    chmod 777 /tmp/mifapi_temp && \
    ln -s /tmp/mifapi_temp /html/getfile && \
    nginx -t && \
    python -m pip install pytest certbot certbot-nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    openssl dhparam -out /etc/nginx/dhparam.pem 2048

COPY nginx.conf /etc/nginx/nginx.conf
COPY ./app /app/

EXPOSE 443