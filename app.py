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
def handler(bucket):
    # is_create = request.args.get('create')
    if request.method == 'POST':

        # //test// 
        buckets = mongo.db.buckets
        return str(buckets.find_one({"name":"yum"}) is None)

        # timeStamp = int(time.time())
        # n = buckets.insert_one({'_id' : bucket,'created' : timeStamp,'modified':timeStamp})
        # return str(n)

        # TODO: really create bucket somtin with database
        # half done :)
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

if __name__=='__main__':
    app.run(debug=True)    