docker build -t varnav/mifapi --progress=plain .
docker run --rm -it --tmpfs /tmp/mifapi_temp -v /etc/letsencrypt:/etc/letsencrypt --entrypoint /app/pytest.sh varnav/mifapi
docker push varnav/mifapi