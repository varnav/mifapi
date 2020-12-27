#!/bin/bash -ex
docker pull varnav/mifapi
docker run --rm -it --tmpfs /tmp/mifapi_temp --entrypoint /app/pytest.sh varnav/mifapi