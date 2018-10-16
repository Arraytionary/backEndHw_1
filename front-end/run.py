from flask import Flask, render_template, request
import requests
import os
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app, support_credentials=True)

C_HOST = os.getenv("CONTROLLER_HOST", "localhost")
C_PORT = os.getenv("CONTROLLER_PORT", 5000)
CONTROLLER_URL = f"http://{C_HOST}:{C_PORT}"
# CONTROLLER_URL = "http://178.128.21.41:5000"

S_HOST = os.getenv("SOS_HOST", "localhost")
S_PORT = os.getenv("SOS_PORT", 8000)
SOS_URL = f"http://{S_HOST}:{S_PORT}"
# SOS_URL = "http://178.128.21.41:8000"


def list_all_bucket():
    resp = requests.get(f"{SOS_URL}/buckets")
    jsonData = resp.json()
    buckets = jsonData["buckets"]
    return buckets

@app.route('/<bucket_name>/display')
def show_gif(bucket_name):
    resp = requests.get(f"{SOS_URL}/{bucket_name}?list")
    jsonData = resp.json()
    objects = jsonData["objects"]
    listobj = []
    for obj in objects:
        # print(obj['name'].split(".")[-1])
        if obj['name'].split(".")[-1].lower() == "gif":
            listobj.append((obj['name'], f"{SOS_URL}/{bucket_name}/{obj['name']}", f"{SOS_URL}/{bucket_name}/{obj['name']}?delete"))
    return render_template('showgif.html', host=request.host, bucketname=bucket_name, listrender=listobj)

@app.route('/<bucket_name>/show_all_videos')
def show_vid(bucket_name):
    buckets = list_all_bucket()

    resp = requests.get(f"{SOS_URL}/{bucket_name}?list")
    jsonData = resp.json()
    objects = jsonData["objects"]
    listobj = []
    for obj in objects:
        if obj['name'].split(".")[-1].lower() in ("mp4", "mov", "avi"):
            listobj.append((obj['name'], bucket_name, f"{CONTROLLER_URL}/makegif"))
    
    return render_template("show.html", host=request.host, buckets=buckets, display=bucket_name+"/display", bucketname=bucket_name, listrender=listobj, make_all=f"{CONTROLLER_URL}/makegif")

# @app.context_processor
# def example():
#     return "sugoi"

if __name__ == '__main__':
   app.run(host='0.0.0.0')