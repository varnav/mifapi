import time

from fastapi.testclient import TestClient
from PIL import Image
from main import app

client = TestClient(app)

# Generate test image
img = Image.new('RGB', (128, 128), color='white')
img.save('/tmp/testimage1.jpg')
img.save('/tmp/testimage2.jpg')
img.save('/tmp/testimage3.jpg')


def test_version():
    response = client.get("/api/v1/version")
    assert response.status_code == 200

def test_jxl_encode():
    files = {'file': open('/tmp/testimage1.jpg', 'rb')}
    response = client.post('/api/v1/jxl/encode', files=files)
    assert response.status_code == 200
    # assert response.json() == {
    #     "id": "foobar",
    #     "title": "Foo Bar"
    # }

def test_jxl_encode_fileexists():
    files = {'file': open('/tmp/testimage1.jpg', 'rb')}
    response = client.post('/api/v1/jxl/encode', files=files)
    assert response.status_code == 409
    # assert response.json() == {
    #     "id": "foobar",
    #     "title": "Foo Bar"
    # }

def test_jxl_encodeasync():
    files = {'file': open('/tmp/testimage2.jpg', 'rb')}
    response = client.post('/api/v1/jxl/encodeasync', files=files)
    assert response.status_code == 200
    # assert response.json() == {
    #     "id": "foobar",
    #     "title": "Foo Bar"
    # }

def test_avif_encodeasync():
    files = {'file': open('/tmp/testimage3.jpg', 'rb')}
    response = client.post('/api/v1/avif/encodeasync?codec=aom', files=files)
    assert response.status_code == 200
    # assert response.json() == {
    #     "id": "foobar",
    #     "title": "Foo Bar"
    # }

def test_download_1():
    time.sleep(10)
    response = client.get("/getfile/testimage1.jxl")
    assert response.status_code == 200


def test_download_2():
    response = client.get("/getfile/testimage2.jxl")
    assert response.status_code == 200


def test_download_3():
    response = client.get("/getfile/testimage3.avif")
    assert response.status_code == 200