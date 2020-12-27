import datetime
import mimetypes
import os
import pathlib
import tempfile
import time
from subprocess import run
from urllib import parse

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

__version__ = '0.2.2'
TTL = 300
JXL_SUPPORTED_FORMATS = ['jpeg', 'jpg', 'png', 'apng', 'gif', 'exr', 'ppm', 'pfm', 'pgx']
AVIF_SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "y4m"]

# Scheduler
executors = {
    'default': ProcessPoolExecutor(20)
}
scheduler = BackgroundScheduler(executors=executors)
scheduler.start()
app = FastAPI(title="mifapi: Modern Image Formats (JPEG XL and AVIF) API", version=__version__, openapi_url="/api/v1/openapi.json")

mimetypes.init()
mimetypes.add_type('image/jxl', '.jxl')

tempdir = tempfile.gettempdir() + os.sep + 'mifapi_temp'

if not os.path.exists(tempdir):
    os.mkdir(tempdir)
app.mount(app.root_path + "/getfile", StaticFiles(directory=tempdir))

try:
    jobs = len(os.sched_getaffinity(0)) - 1
except AttributeError:
    jobs = 1
if jobs == 0:
    jobs = 1


def cleanup(file1, file2):
    print('Deleting:', file1, file2)
    os.remove(file1)
    os.remove(file2)


def encodejxl(fp, newpath):
    print("Async encode", fp, newpath)
    speed = 'kitten'
    convert_cmd = f'/usr/bin/cjxl -s {speed} --num_threads={jobs} "{fp}" "{newpath}"'
    print(convert_cmd)
    run(convert_cmd, shell=True)


def encodeavif(fp, newpath, codec):
    """

    :type codec: ['aom', 'svt', 'rav1e']
    """
    print("Async encode", fp, newpath, codec)
    speed = 9
    convert_cmd = f'avifenc -j {jobs} -c {codec} -s {speed} {fp} -o {newpath}'
    print(convert_cmd)
    run(convert_cmd, shell=True)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/api/v1/version")
def version():
    return {"ver": __version__, "cjxl_ver": run(['cjxl', '--version'], capture_output=True).stdout, "avifenc_ver": run(['avifenc', '--version'], capture_output=True).stdout}


class Encoded(BaseModel):
    bytes_saved: int
    dl_uri: str
    file_ttl_sec: int = TTL


class EncodedNosize(BaseModel):
    dl_uri: str
    file_ttl_sec: int = TTL


class Decoded(BaseModel):
    dl_uri: str
    file_ttl_sec: int = TTL


@app.post("/api/v1/jxl/encode", response_model=Encoded, description="Encode file into jxl (lossless if JPEG)")
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
        speed = 'kitten'
        convert_cmd = f'/usr/bin/cjxl --quiet -s {speed} --num_threads={jobs} "{fp}" "{newpath}"'
        print(convert_cmd)
        job = run(convert_cmd, shell=True)
        if job.returncode == 0:
            saved = os.path.getsize(fp) - os.path.getsize(newpath)
            scheduler.add_job(cleanup, 'date', args=[fp, newpath], next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=TTL))
            return {"bytes_saved": saved, "dl_uri": str(request.base_url) + 'getfile/' + parse.quote(str(newfilename)), "file_ttl_sec": TTL}
        else:
            raise HTTPException(status_code=500, detail="Conversion error")


@app.post("/api/v1/jxl/encodeasync", response_model=EncodedNosize, description="Async encode file into jxl (lossless if JPEG)")
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
        scheduler.add_job(encodejxl, 'date', args=[fp, newpath], next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=2))
        scheduler.add_job(cleanup, 'date', args=[fp, newpath], next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=TTL))
        return {"dl_uri": str(request.base_url) + 'getfile/' + parse.quote(str(newfilename)), "file_ttl_sec": TTL}


@app.post("/api/v1/avif/encodeasync", response_model=EncodedNosize, description="Async encode file into AVIF")
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
        scheduler.add_job(encodeavif, 'date', args=[fp, newpath, codec], next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=2))
        scheduler.add_job(cleanup, 'date', args=[fp, newpath], next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=TTL))
        return {"dl_uri": str(request.base_url) + 'getfile/' + parse.quote(str(newfilename)), "file_ttl_sec": TTL}


@app.post("/api/v1/jxl/decode", response_model=Decoded, description="Lossless decode jxl into jpeg")
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
            saved = os.path.getsize(fp) - os.path.getsize(newpath)
            scheduler.add_job(cleanup, 'date', args=[fp, newpath], next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=TTL))
            return {"bytes_saved": saved, "dl_uri": str(request.base_url) + 'getfile/' + parse.quote(str(newfilename)), "file_ttl_sec": TTL}
        else:
            raise HTTPException(status_code=500, detail="Conversion error")
