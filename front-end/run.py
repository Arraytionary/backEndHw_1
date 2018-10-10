from flask import Flask, render_template, request
import requests
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


@app.route('/<bucket_name>/display')
def student(bucket_name):
    resp = requests.get("http://178.128.21.41:8000/boat?list")
    jsonData = resp.json()
    objects = jsonData["objects"]
    listobj = []
    for obj in objects:
        # print(obj['name'].split(".")[-1])
        if obj['name'].split(".")[-1].lower() == "gif":
            listobj.append((obj['name'], f"http://178.128.21.41:8000/{bucket_name}/{obj['name']}"))
    return render_template('showgif.html', listrender=listobj)

@app.route('/<bucket_name>/show_all_videos')
def show(bucket_name):

    resp = requests.get("http://178.128.21.41:8000/boat?list")
    jsonData = resp.json()
    objects = jsonData["objects"]
    listobj = []
    for obj in objects:
        if obj['name'].split(".")[-1].lower() in ("mp4", "mov", "avi"):
            listobj.append((obj['name'], bucket_name, f"http://178.128.21.41:5000/makegif"))
    
    return render_template("show.html", display=bucket_name+"/display", bucketname=bucket_name, listrender=listobj, make_all=f"http://178.128.21.41:5000/makegif")

# @app.context_processor
# def example():
#     return "sugoi"

if __name__ == '__main__':
   app.run(debug = True)