from flask import Flask, url_for,request,jsonify
import re
app = Flask(__name__)

buckets = set()

@app.route('/')
def index():
    return 'hello, World!'

# @app.route('/<bucketName>',methods=['POST'])
# def create(bucketName):
#     jsonify({"created":,"modified":,"name":(str)bucketName})
#     request.args.get()
#     return 'bucket %s created' % lol

@app.route('/<path:query>')
def handler(query):
    url = request.url
    url = url[url.replace('//','xx').find('/')+1:] #strip just url after /
    matchCreate = re.match(r'^.+\?create$',url)
    if(not '/' in url):
        if(matchCreate.group()):
            bucketName = matchCreate.group()
            bucketName = bucketName[:bucketName.find("?create")]
            json = create(bucketName)
            if(json):
                return json      

def create(bucketName):
    def addBucket(bucketName):
        bucketsSize = len(buckets)
        buckets.add(bucketName)
        return not bucketsSize == len(buckets)

    #create bucket return json, 200 if success!!
    if(addBucket(bucketName)):
        return jsonify({"created":0,"modified":1,"name":bucketName})

    