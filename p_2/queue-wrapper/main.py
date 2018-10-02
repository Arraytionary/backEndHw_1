import os
import json
import redis
from flask import Flask, jsonify, request
HOST = os.getenv("SOS_HOST", "localhost")
PORT = os.getenv("SOS_PORT", 8000)
BASE_URL = f"{HOST}:{PORT}"

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
    if file_name == "":
        mode = 1
    json_packed = json.dumps(body)
    RedisResource.conn.rpush(
        RedisResource.QUEUE_NAME,
        json_packed)

    return jsonify({'status': 'OK'})
