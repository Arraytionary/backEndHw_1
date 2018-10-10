#!/usr/bin/env python3
import hashlib
import os
import logging
import json
import uuid
import redis
import requests

HOST = os.getenv("SOS_HOST", "localhost")
PORT = os.getenv("SOS_PORT", 8000)
BASE_URL = f"http://{HOST}:{PORT}"


LOG = logging
REDIS_QUEUE_LOCATION = os.getenv('REDIS_QUEUE', 'localhost')
QUEUE_NAME = 'queue'

INSTANCE_NAME = uuid.uuid4().hex

LOG.basicConfig(
    level=LOG.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def watch_queue(redis_conn, queue_name, callback_func, timeout=30):
    active = True

    while active:
        # Fetch a json-encoded task using a blocking (left) pop
        packed = redis_conn.blpop([queue_name], timeout=timeout)

        if not packed:
            # if nothing is returned, poll a again
            continue

        _, packed_task = packed

        # If it's treated to a poison pill, quit the loop
        if packed_task == b'DIE':
            active = False
        else:
            task = None
            try:
                task = json.loads(packed_task)
            except Exception:
                LOG.exception('json.loads failed')
            if task:
                callback_func(task)

def execute(log, task):
    log.info(str(task))
    # number = task.get('number')
    file_name = task.get("file_name")
    bucket_name = task.get("bucket_name")
    text = task.get("text")
    # mode = int(task.get("mode"))
    # if mode == 0:
    make_gif(bucket_name, file_name, text)

def make_gif(bucket_name, file_name, text):
    file = requests.get(f"{BASE_URL}/{bucket_name}/{file_name}", headers={"Range":"byte=0-"})
    md5 = hashlib.md5()

    #download video from sos
    with open(f"./{file_name}", "wb") as fo:
        for con in file.iter_content(chunk_size=256):
            fo.write(con)

    #run make_thumbnail script
    os.system(f"./make_thumbnail {file_name} {file_name}.gif {text}")

    #delete file odwnloaded from sos
    os.remove(f"./{file_name}")

    #compute md5
    with open(f"./{file_name}.gif", "rb") as data: 
        for chunk in iter(lambda: data.read(4096), b""):
            md5.update(chunk)
    #create upload ticket
    requests.post(f"{BASE_URL}/{bucket_name}/{file_name}.gif?create")
    #upload gif
    requests.put(f"{BASE_URL}/{bucket_name}/{file_name}.gif?partNumber=1",data=open(f"./{file_name}.gif","rb"), headers={"Content-MD5":f"{md5.hexdigest()}"})
    #issue complete to sos
    requests.post(f"{BASE_URL}/{bucket_name}/{file_name}.gif?complete")

    #delete gif on local
    os.remove(f"./{file_name}.gif")


def make_all_gif(bucket_name):    
    pass

def main():
    LOG.info('Starting a worker...')
    LOG.info('Unique name: %s', INSTANCE_NAME)
    host, *port_info = REDIS_QUEUE_LOCATION.split(':')
    port = tuple()
    if port_info:
        port, *_ = port_info
        port = (int(port),)

    named_logging = LOG.getLogger(name=INSTANCE_NAME)
    named_logging.info('Trying to connect to %s [%s]', host, REDIS_QUEUE_LOCATION)
    redis_conn = redis.Redis(host=host, *port)
    watch_queue(
        redis_conn, 
        QUEUE_NAME, 
        lambda task_descr: execute(named_logging, task_descr))

