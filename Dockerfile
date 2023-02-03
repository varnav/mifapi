FROM python:3.10-bullseye as builder

COPY ./build_avif.sh .
RUN /bin/bash ./build_avif.sh

COPY ./build_cjxl.sh .
RUN /bin/bash ./build_cjxl.sh

# Docs https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

LABEL Maintainer = "Evgeny Varnavskiy <varnavruz@gmail.com>"
LABEL Description="mifapi: Modern Image Formats (JPEG XL and AVIF) Web API"
LABEL License="MIT License"

LABEL org.label-schema.schema-version="1.0"
#LABEL org.label-schema.url="https://avif.photos"
LABEL org.label-schema.vcs-url="https://github.com/varnav/mifapi"
LABEL org.label-schema.docker.cmd="docker run -d --name mifapi --restart on-failure:10 --security-opt no-new-privileges --tmpfs /tmp/mifapi_temp -p 80:80 -p 443:443 -v /etc/letsencrypt:/etc/letsencrypt mycoolcompany/mifapi"
LABEL org.label-schema.docker.cmd.test="docker run --rm -it --tmpfs /tmp/mifapi_temp --entrypoint /app/pytest.sh varnav/mifapi"

ENV PORT=8000
ENV DEBIAN_FRONTEND=noninteractive
#ENV ACCESS_LOG=/var/log/gunicorn/access.log
#ENV ERROR_LOG=/var/log/gunicorn/error.log

# Compile with forced AVX2 support (conservative)
ENV RUSTFLAGS="-C target-feature=+avx2,+fma"
ENV CFLAGS="-mavx2 -mfma -ftree-vectorize -pipe"

# Compile for current CPU only - may increase performance
# ENV RUSTFLAGS="-C target-cpu=native"
# ENV CFLAGS="-march=native -pipe"

ENV CXXFLAGS="${CFLAGS}"

COPY --from=builder /tmp/libjxl/build/tools/djxl /tmp/libjxl/build/tools/cjxl /tmp/libavif/build/avifenc /usr/bin/
COPY --from=builder /tmp/libjxl/build/*.so* /usr/local/lib/

COPY ./pyproject.toml .

RUN set -ex && \
    mkdir /html && \
    python -m pip install --no-cache-dir -U pip && \
    python -m pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install

RUN apt-get update && apt-get install --no-install-recommends -y libgif-dev nginx software-properties-common ca-certificates && \
    mkdir /tmp/mifapi_temp && \
    mkdir /var/log/gunicorn && \
    chmod 777 /tmp/mifapi_temp && \
    ln -s /tmp/mifapi_temp /html/getfile && \
    nginx -t && \
    python -m pip install --no-cache-dir tailon pytest certbot certbot-nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN openssl dhparam -out /etc/nginx/dhparam.pem 2048

COPY ./html /html/
COPY nginx.conf /etc/nginx/nginx.conf
COPY ./app/main.py ./app/prestart.sh ./app/pytest.sh ./app/test_main.py /app/

EXPOSE 443