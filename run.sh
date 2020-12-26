mkdir /etc/letsencrypt
docker stop mifapi && docker rm mifapi && docker pull varnav/mifapi
docker run -d --name mifapi --tmpfs /tmp/mifapi_temp -p 80:80 -p 443:443 -v /etc/letsencrypt:/etc/letsencrypt varnav/mifapi
docker logs -f mifapi
