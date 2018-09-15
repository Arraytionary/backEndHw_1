from flask import Flask, url_for,request,jsonify
from flask_pymongo import PyMongo
from werkzeug.exceptions import BadRequest
import re,time,requests,pymongo


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mango'
app.config['MONGO_URI'] = 'mongodb://admin:passw0rd@ds257372.mlab.com:57372/mango'

mongo = PyMongo(app)

# buckets = set()

@app.route('/')
def index():
    return 'hello, World!'

# @app.route('/<bucketName>',methods=['POST'])
# def create(bucketName):
#     jsonify({"created":,"modified":,"name":(str)bucketName})
#     request.args.get()
#     return 'bucket %s created' % lol

@app.route('/<bucket>',methods = ['POST','GET','DELETE'])
def bucketHandler(bucket):
    # is_create = request.args.get('create')
    if request.method == 'POST':

        # //test// 
        # buckets = mongo.db.buckets
        # return str(buckets.find_one({"name":"yum"}) is None)

        # timeStamp = int(time.time())
        # n = buckets.insert_one({'_id' : bucket,'created' : timeStamp,'modified':timeStamp})
        # return str(n)

        # TODO: really create bucket somtin with database
        # half done :)
        if request.args.get('create') is not None:
            json = createBucket(bucket)
            if(json):
                return json
            else: 
                raise BadRequest()

    elif request.method == 'DELETE':
        # TODO: really delete bucket
        if request.args.get('delete') is not None:
            if(delete(bucket)):
                return "yay delete %s complete" %bucket
            else:
                return BadRequest()

    elif request.method == 'GET':
        if request.args.get('list') is not None:
            json = listOut(bucket)
            if(json):
                return json
            else:
                raise BadRequest()
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
def createBucket(bucketName):
    def addBucket(bucketName,timeStamp):
        #This is the version of python set()
        # bucketsSize = len(buckets)
        # buckets.add(bucketName)
        # return not bucketsSize == len(buckets)

        bucket = mongo.db.buckets
        #Try to create new bucket with a unique bucket name
        try:
            bucket.insert_one({'_id' : bucketName,'created' : timeStamp,'modified':timeStamp})
            return True
        #Bucket's name already exist in the db
        except pymongo.errors.DuplicateKeyError:
            return False

    #create bucket return json, 200 if success!!
    timeStamp = int(time.time())
    if(addBucket(bucketName,timeStamp)):
        return jsonify({"created":timeStamp,"modified":timeStamp,"name":bucketName})

def delete(bucketName):
    # this is python set() version
    # if bucketName in buckets:
    #     buckets.remove(bucketName)
    #     return True
    # else:
    #     return False

    bucket = mongo.db.buckets
    result = bucket.find_one({"_id":bucketName})
    if(result):
        bucket.remove(result)
        return True
    else:
        return False

def listOut(bucketName):
    if bucketName in buckets:
        # TODO: return jsonify of list of things in bucket add anothyer collection into ?create
        return True

@app.route('/<bucketName>/<object>',methods = ['POST','GET','DELETE','PUT'])
def objectHandler(bucketName,object):
    if request.method == 'POST':
        if request.args.get('create') is not None:
            if createObject(bucketName,object):
                return "success"
            else:
                raise BadRequest()
    elif request.method == 'PUT':
        #if for checking upload al part
        if(int(request.args.get("partNumber")) == 1):
            md5 = request.form.get("Content-MD5")
            length = request.form.get("Content-Length")
            json = uploadAllpart(bucketName,object,length,md5)
            if(json):
                return json
            else:
                return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"LengthMismatched|MD5Mismatched|InvalidPartNumber|InvalidObjectName|InvalidBucket"})

        if(int(request.args.get("partNumber")) > 1 and int(request.args.get("partNumber")) <= 10000):
            # upload multi part
            pass


def createObject(bucketName,object):
    bucket = mongo.db.buckets
    if bucket.find_one({"_id":bucketName}):
        bucket = mongo.db[bucketName]

        exist = bucket.find_one({"_id":object})
        if(not exist):
            bucket.insert_one({"_id":object,"complete":False})
            # do a bunch more thingssssssss
            return True
    return False

def uploadAllpart(bucketName,object,length,md5):
    bucket = mongo.db.buckets
    if bucket.find_one({"_id":bucketName}):
        bucket = mongo.db[bucketName]

        exist = bucket.find_one({"_id":object})
        if(exist):
            if not exist["complete"]:
                return jsonify({"md5":md5,'length':length,"partNumber":1})


if __name__=='__main__':
    app.run(debug=True)    