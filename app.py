from flask import Flask, url_for,request,jsonify
from werkzeug.exceptions import BadRequest
import re,time,requests
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

@app.route('/<bucket>',methods = ['POST','GET','DELETE'])
def handler(bucket):
    # is_create = request.args.get('create')
    if request.method == 'POST':
        # TODO: really create bucket somtin with database
        if request.args.get('create') is not None:
            json = create(bucket)
            if(json):
                return json
            else: 
                raise BadRequest()

    if request.method == 'DELETE':
        # TODO: really delete bucket
        if request.args.get('delete') is not None:
            if(delete(bucket)):
                return "yay delete %s complete" %bucket
            else:
                return BadRequest()

    if request.method == 'GET':
        if request.args.get('list') is not None:
            json = listOut(bucket)
            if(json):
                return json
            else:
                raise BadRequest()

    # url = request.url
    # url = url[url.replace('//','xx').find('/')+1:] #strip just url after /
    # matchCreate = re.match(r'^.+\?create$',url)
    # matchDelete = re.match(r'^.+\?delete$',url)
    # if(not '/' in url):
    #     if(matchCreate.group()):
    #         bucketName = matchCreate.group()
    #         bucketName = bucketName[:bucketName.find("?create")]
    #         json = create(bucketName)
    #         if(json):
    #             return json     
def create(bucketName):
    def addBucket(bucketName):
        bucketsSize = len(buckets)
        buckets.add(bucketName)
        return not bucketsSize == len(buckets)

    #create bucket return json, 200 if success!!
    if(addBucket(bucketName)):
        timeStamp = int(time.time())
        return jsonify({"created":timeStamp,"modified":timeStamp,"name":bucketName})

def delete(bucketName):
    if bucketName in buckets:
        buckets.remove(bucketName)
        return True
    else:
        return False

def listOut(bucketName):
    if bucketName in buckets:
        # TODO: return jsonify of list of things in bucket
        

    