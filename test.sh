#!/bin/bash -ex
docker pull varnav/mifapi
docker run --rm -it --tmpfs /tmp/mifapi_temp -v /etc/letsencrypt:/etc/letsencrypt --entrypoint /app/pytest.sh varnav/mifapi