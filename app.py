from flask import Flask, url_for,request,jsonify
from flask_pymongo import PyMongo
from werkzeug.exceptions import BadRequest
import re,time,requests,pymongo,os,sys,hashlib


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mango'
app.config['MONGO_URI'] = 'mongodb://admin:passw0rd@ds257372.mlab.com:57372/mango'

mongo = PyMongo(app)

# buckets = set()

@app.route('/',methods = ["PUT"])
def index():
    if request.method == 'PUT':
        path = "yummy"
        os.makedirs(path)
        data = request.get_data()
        with open("yummy/abc.txt","wb") as fo:
            fo.write(request.data)
        fo.close()
        return ""

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
                path = bucket
                os.mkdir(path,777)
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

        elif request.args.get('complete') is not None:
            # TODO: STEP3 stuff
            pass

    elif request.method == 'PUT':
        #if for checking upload al part
        if(int(request.args.get("partNumber")) in range(1,10001)):
            data = request.get_data()

            objectData = request.data
            m = hashlib.md5()
            m.update(objectData)
            m.hexdigest()
            return str(m.hexdigest())

            md5 = request.headers.get("Content-MD5")
            length = request.headers.get("Content-Length")

            json = upload(data,bucketName,object,length,md5)
            if(json):
                return json
            else:
                return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"LengthMismatched|MD5Mismatched|InvalidPartNumber|InvalidObjectName|InvalidBucket"})

        if(int(request.args.get("partNumber")) in range(1,10001)):
            # upload multi part
            pass

    elif request.method == 'DELETE':
        if request.args.get("partNumber") is not None:
            if deleteObject(bucketName,object):
                return success
            else:
                raise BadRequest


        


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

def upload(data,bucketName,object,length,md5):
    bucket = mongo.db.buckets
    if bucket.find_one({"_id":bucketName}):
        bucket = mongo.db[bucketName]
        exist = bucket.find_one({"_id":object})
        if(exist):
            if not exist["complete"]:
                objectData = request.data
                m = hashlib.md5()
                m.update(objectData)
                if m.hexdigest() == md5:
                #contentlength condition


                    #TODO: write file in the right folder
                    path = "yummy"
                    os.makedirs(path)
                    data = request.get_data()
                    with open("yummy/abc.txt","wb") as fo:
                        fo.write(request.data)
                    fo.close()
                    return jsonify({"md5":md5,'length':length,"partNumber":1})
            else:
                return "Object"
        else:
            return "InvalidObjectName"
    else:
        return "InvalidBucket"

def deleteObject(bucketName,object):
    bucket = mongo.db.buckets
    if bucket.find_one({"_id":bucketName}):
        bucket = mongo.db[bucketName]

        obj = bucket.find_one({"_id":object})
        if(obj):
            bucket.remove(obj)
            return True
    return False


if __name__=='__main__':
    app.run(debug=True)    