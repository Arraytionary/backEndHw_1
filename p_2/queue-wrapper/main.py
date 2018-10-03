import os
import json
import redis
import requests
from flask import Flask, jsonify, request
HOST = os.getenv("SOS_HOST", "localhost")
PORT = os.getenv("SOS_PORT", 8000)
BASE_URL = f"http://{HOST}:{PORT}"

app = Flask(__name__)

class RedisResource:
    REDIS_QUEUE_LOCATION = os.getenv('REDIS_QUEUE', 'localhost')
    QUEUE_NAME = 'queue'

    host, *port_info = REDIS_QUEUE_LOCATION.split(':')
    port = tuple()
    if port_info:
        port, *_ = port_info
        port = (int(port),)

    conn = redis.Redis(host=host, *port)

@app.route('/factor', methods=['POST'])
def post_factor_job():
    body = request.json
    json_packed = json.dumps(body)
    print('packed:', json_packed)
    RedisResource.conn.rpush(
        RedisResource.QUEUE_NAME,
        json_packed)
    
    return jsonify({'status': 'OK'})

@app.route('/makegif', methods = ['POST'])
def post_make_gif():
    body = request.json
    bucket_name = body["bucket"]
    file_name = body["file"]
    mode = 0

    if not bucket_name and file_name is None:
        return jsonify({'status': 'JSON MISMATCH'}),404
    
    if file_name == "":
        mode = 1        
    resp = requests.get(f"{BASE_URL}/{bucket_name}?list")
    if resp.status_code == 400:
        return jsonify({'status': 'BUCKET NOT FOUND'}),404
    if mode == 0:    
        resp = requests.get(f"{BASE_URL}/validate/{bucket_name}/{file_name}")
        if resp.status_code == 404:
            return jsonify({'status': 'FILE NOT FOUND'}),404
    objects = resp.json()["objects"]
    json_packed = json.dumps({"bucket_name":bucket_name, "file_name":file_name, "mode":mode})
    RedisResource.conn.rpush(
        RedisResource.QUEUE_NAME,
        json_packed)

    return jsonify({'status': 'OK'})
