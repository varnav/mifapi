import datetime
import mimetypes
import os
import pathlib
import tempfile
import time
from subprocess import run
from urllib import parse

import pytz
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

__version__ = '0.3.1'
TTL = 40
JXL_SUPPORTED_FORMATS = ['jpeg', 'jpg', 'png', 'apng', 'gif', 'exr', 'ppm', 'pfm', 'pgx']
AVIF_SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "y4m"]

app = FastAPI(title="mifapi: Modern Image Formats (JPEG XL and AVIF) Web API", version=__version__, openapi_url="/api/v1/openapi.json")

print("Starting mifapi", __version__)

mimetypes.init()
mimetypes.add_type('image/jxl', '.jxl')

tempdir = tempfile.gettempdir() + os.sep + 'mifapi_temp'

# Static files are normally handled by nginx in the Docker container. This is for testing and development.
if not os.path.exists(tempdir):
    os.mkdir(tempdir)
app.mount(app.root_path + "/getfile", StaticFiles(directory=tempdir))

try:
    jobs = len(os.sched_getaffinity(0)) - 1
except AttributeError:
    jobs = 1
if jobs == 0:
    jobs = 1


def cleanup():
    i = 0
    for f in os.listdir(tempdir):
        fullpath = os.path.join(tempdir, f)
        if os.stat(fullpath).st_mtime < time.time() - TTL:
            print('Deleting:', fullpath)
            os.remove(fullpath)
            i += i
    return i


# schedule.every(30).seconds.do(cleanup)

# Scheduler
executors = {
    'default': ProcessPoolExecutor(20)
}
scheduler = BackgroundScheduler(executors=executors)
scheduler.start()

scheduler.add_job(cleanup, 'interval', minutes=2)


def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')


scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)


def encodejxl(fp, newpath):
    print("Encode", fp, newpath)
    speed = 'kitten'
    convert_cmd = f'/usr/bin/cjxl -s {speed} --num_threads={jobs} "{fp}" "{newpath}"'
    print(convert_cmd)
    job = run(convert_cmd, shell=True)
    if job.returncode == 0:
        saved = os.path.getsize(fp) - os.path.getsize(newpath)
        return saved
    else:
        raise HTTPException(status_code=500, detail="Conversion error")


def encodeavif(fp, newpath, codec):
    """

    :type codec: ['aom', 'svt', 'rav1e']
    """
    print("Encode", fp, newpath, codec)
    speed = 9
    convert_cmd = f'avifenc -d 8 -y 420 -j {jobs} -c {codec} -s {speed} {fp} -o {newpath}'
    print(convert_cmd)
    job = run(convert_cmd, shell=True)
    if job.returncode == 0:
        saved = os.path.getsize(fp) - os.path.getsize(newpath)
        return saved
    else:
        raise HTTPException(status_code=500, detail="Conversion error")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


class Version(BaseModel):
    ver: str = __version__
    cjxl_ver: str
    avifenc_ver: str


class Encoded(BaseModel):
    bytes_saved: int
    dl_uri: str
    file_expires: str


class EncodedNosize(BaseModel):
    dl_uri: str
    file_expires: str


class Decoded(BaseModel):
    bytes_lost: int
    dl_uri: str
    file_expires: str


@app.get("/api/v1/version", response_model=Version, summary="Return versions of used libraries")
def version():
    return {"ver": __version__, "cjxl_ver": run(['cjxl', '--version'], capture_output=True).stdout, "avifenc_ver": run(['avifenc', '--version'], capture_output=True).stdout}


@app.get("/api/v1/cleanup", summary="Force cleanup job")
def version():
    files_cleaned = cleanup()
    return {"files_cleaned": files_cleaned}


@app.post("/api/v1/jxl/encode", response_model=Encoded, summary="Encode file into jxl (lossless if JPEG)")
def encode_jxl(request: Request, file: UploadFile = File(...)):
    extension = os.path.splitext(file.filename)[1][1:]
    if extension.lower() not in JXL_SUPPORTED_FORMATS:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    fp = pathlib.PurePath(tempdir + os.sep + file.filename)
    newfilename = str(fp.stem) + '.' + 'jxl'
    newpath = tempdir + os.sep + newfilename
    if os.path.exists(newpath) or os.path.exists(fp):
        raise HTTPException(status_code=409, detail="File exists")
    else:
        f = open(fp, 'wb')
        f.write(file.file.read())
        f.close()
        saved = encodejxl(fp, newpath)
        expires = (datetime.datetime.now() + datetime.timedelta(seconds=TTL)).replace(tzinfo=pytz.UTC)
        return {"bytes_saved": saved, "dl_uri": str(request.base_url) + 'getfile/' + parse.quote(str(newfilename)), "file_expires": expires.isoformat()}


@app.post("/api/v1/jxl/encodeasync", response_model=EncodedNosize, summary="Async encode file into jxl (lossless if JPEG)")
async def encode_jxl_async(request: Request, file: UploadFile = File(...)):
    extension = os.path.splitext(file.filename)[1][1:]
    if extension.lower() not in JXL_SUPPORTED_FORMATS:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    fp = pathlib.PurePath(tempdir + os.sep + file.filename)
    newfilename = str(fp.stem) + '.' + 'jxl'
    newpath = tempdir + os.sep + newfilename
    if os.path.exists(newpath) or os.path.exists(fp):
        raise HTTPException(status_code=409, detail="File exists")
    else:
        f = open(fp, 'wb')
        f.write(file.file.read())
        f.close()
        expires = (datetime.datetime.now() + datetime.timedelta(seconds=TTL)).replace(tzinfo=pytz.UTC)
        scheduler.add_job(encodejxl, trigger='date', args=[fp, newpath], next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=2))
        return {"dl_uri": str(request.base_url) + 'getfile/' + parse.quote(str(newfilename)), "file_expires": expires.isoformat()}


@app.post("/api/v1/avif/encode", response_model=EncodedNosize, summary="Async encode file into AVIF")
async def encode_avif(request: Request, file: UploadFile = File(...), codec: str = 'aom'):
    extension = os.path.splitext(file.filename)[1][1:]
    if extension.lower() not in AVIF_SUPPORTED_FORMATS:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    fp = pathlib.PurePath(tempdir + os.sep + file.filename)
    newfilename = str(fp.stem) + '.' + 'avif'
    newpath = tempdir + os.sep + newfilename
    if os.path.exists(newpath) or os.path.exists(fp):
        raise HTTPException(status_code=409, detail="File exists")
    else:
        f = open(fp, 'wb')
        f.write(file.file.read())
        f.close()
        saved = encodeavif(fp, newpath, codec)
        expires = (datetime.datetime.now() + datetime.timedelta(seconds=TTL)).replace(tzinfo=pytz.UTC)
        return {"bytes_saved": saved, "dl_uri": str(request.base_url) + 'getfile/' + parse.quote(str(newfilename)), "file_expires": expires.isoformat()}


@app.post("/api/v1/avif/encodeasync", response_model=EncodedNosize, summary="Async encode file into AVIF")
async def encode_avif_async(request: Request, file: UploadFile = File(...), codec: str = 'aom'):
    extension = os.path.splitext(file.filename)[1][1:]
    if extension.lower() not in AVIF_SUPPORTED_FORMATS:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    fp = pathlib.PurePath(tempdir + os.sep + file.filename)
    newfilename = str(fp.stem) + '.' + 'avif'
    newpath = tempdir + os.sep + newfilename
    if os.path.exists(newpath) or os.path.exists(fp):
        raise HTTPException(status_code=409, detail="File exists")
    else:
        f = open(fp, 'wb')
        f.write(file.file.read())
        f.close()
        expires = (datetime.datetime.now() + datetime.timedelta(seconds=TTL)).replace(tzinfo=pytz.UTC)
        scheduler.add_job(encodeavif, 'date', args=[fp, newpath, codec], next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=2))
        return {"dl_uri": str(request.base_url) + 'getfile/' + parse.quote(str(newfilename)), "file_expires": expires.isoformat()}


@app.post("/api/v1/jxl/decode", response_model=Decoded, summary="Lossless decode jxl into jpeg")
def decode_jpg(request: Request, file: UploadFile = File(...)):
    extension = os.path.splitext(file.filename)[1][1:]
    if extension.lower() not in ['jxl']:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    fp = pathlib.PurePath(tempdir + os.sep + file.filename)
    newfilename = str(fp.stem) + '.' + 'jpg'
    newpath = tempdir + os.sep + newfilename
    if os.path.exists(newpath) or os.path.exists(fp):
        raise HTTPException(status_code=409, detail="File exists")
    else:
        f = open(fp, 'wb')
        f.write(file.file.read())
        f.close()
        convert_cmd = f'/usr/bin/djxl --jpeg "{fp}" "{newpath}"'
        print(convert_cmd)
        job = run(convert_cmd, shell=True)
        if job.returncode == 0:
            lost = os.path.getsize(fp) - os.path.getsize(newpath)
            expires = (datetime.datetime.now() + datetime.timedelta(seconds=TTL)).replace(tzinfo=pytz.UTC)
            return {"bytes_lost": lost, "dl_uri": str(request.base_url) + 'getfile/' + parse.quote(str(newfilename)), "file_expires": expires.isoformat()}
        else:
            raise HTTPException(status_code=500, detail="Conversion error")
