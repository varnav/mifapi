$ErrorActionPreference = "Stop"
docker build -t varnav/mifapi --progress=plain . || exit /b
docker run --rm -it --tmpfs /tmp/mifapi_temp --entrypoint /app/pytest.sh varnav/mifapi || exit /b
docker push varnav/mifapi