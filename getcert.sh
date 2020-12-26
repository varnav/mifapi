docker exec -it mifapi /bin/bash
pkill nginx
certbot certonly --standalone -d jxl.photos -d avif.photos
docker restart mifapi