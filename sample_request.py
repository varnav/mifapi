# Sample file conversion with mifapi
# https://github.com/varnav/mifapi
# Evgeny Varnavskiy 2020
# MIT License

import requests
import json

infile = 'c:\\temp\\IMG_20201219_140051.JPG'
outfile = 'c:\\temp\\IMG_20201219_140051.jxl'
url = 'https://avif.photos/api/v1/jxl/encode'

try:
    files = {'file': open(infile, 'rb')}
    getdata = requests.post(url, files=files)
    if getdata.status_code == 200:
        dl_uri = json.loads(getdata.text)["dl_uri"]
        r = requests.get(dl_uri)
        with open(outfile, 'wb') as f:
            f.write(r.content)
    else:
        print("Error:", json.loads(getdata.text)["detail"])
except Exception as e:
    print("Exception:", e)
