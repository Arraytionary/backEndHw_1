from flask import Flask, url_for,request,jsonify,abort
from flask_pymongo import PyMongo
from pymongo import MongoClient
from werkzeug.exceptions import BadRequest,Response
from Utils.object_utils import *
from Utils.file_utils import object_generator
from Utils.bucket_utils import *
import re,time,pymongo,os,sys,hashlib,shutil
import urllib.parse


app = Flask(__name__)


client = MongoClient('mongodb://mongo:27017/')
mongo = client.mango


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

@app.route('/<bucket>',methods = ['POST'])
def bucket_create(bucket):
    # is_create = request.args.get('create')
    if request.args.get('create') == "" and len(request.args) == 1:
        jsonData = createBucket(bucket,mongo)
        if(jsonData):
            return jsonData
        else: 
            raise BadRequest()

@app.route('/<bucket>',methods = ['DELETE'])
def bucket_delete(bucket):
    if request.args.get('delete') == "" and len(request.args) == 1:
        if(delete(bucket,mongo)):
            return "yay delete %s complete" %bucket
        else:
            return BadRequest()

@app.route('/<bucket>',methods = ['GET'])
def bucket_list(bucket):
    if request.args.get('list') == "" and len(request.args) == 1:
        jsonData = listOut(bucket,mongo)
        if(jsonData):
            return jsonData
        else:
            raise BadRequest()

@app.route('/<bucketName>/<objectName>',methods = ['POST'])
def object_POST_handler(bucketName,objectName):
    if request.args.get('create') == "" and len(request.args) == 1:
        if create_object(bucketName,objectName,mongo):
            return "success"
        else:
            raise BadRequest()

    elif request.args.get('complete') == "" and len(request.args) == 1:
        jsonData = complete(bucketName,objectName,mongo)
        if "error" not in jsonData.json:
            return jsonData
        else:
            # raise BadRequest
            return jsonData,400

@app.route('/<bucketName>/<objectName>',methods = ['PUT'])
def object_PUT_handler(bucketName,objectName):
    if request.args.get('metadata') == "" and request.args.get('key') is not None and len(request.args) == 2:
        key = request.args.get('key')
        success = metadata_adder(bucketName,objectName,key,request,mongo)
        if success:
            return "add/update metadata successful"
        else:
            abort(404)

        #if for checking upload al part
    elif request.args.get("partNumber") is not None and len(request.args) == 1:
        if(int(request.args.get("partNumber")) in range(1,10001)):
            data = request.get_data()
            md5 = request.headers.get("Content-MD5")
            length = request.headers.get("Content-Length")

            jsonData = upload(data,bucketName,objectName,length,md5,int(request.args.get("partNumber")),mongo)
            if "error" not in jsonData.json:
                return jsonData
            else:
                # raise BadRequest
                return jsonData,400
        else:
            # raise BadRequest
            return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"InvalidPartNumber"}),400

@app.route('/<bucketName>/<objectName>',methods = ['DELETE'])
def object_DELETE_handler(bucketName,objectName):
    if request.args.get('metadata') == "" and request.args.get('key') is not None and len(request.args) == 2:
        key = request.args.get('key')
        success = metadata_delete(bucketName,objectName,key,mongo)
        if success:
            return "delete successful"
        else:
            abort(404)

    part = request.args.get("partNumber")
    if part is not None:
        if delete_object_by_part(bucketName,objectName,int(part),mongo):
            return "success"
        else:
            raise BadRequest
    elif request.args.get("delete") == "":
        if delete_object(bucketName,objectName,mongo):
            return "success"
        else:
            raise BadRequest()
        
@app.route('/<bucketName>/<objectName>',methods = ['GET'])
def object_GET_handler(bucketName,objectName):
    if request.args.get('metadata') == "" and request.args.get('key') is not None and len(request.args) == 2:
        key = request.args.get('key')
        jsonData = metadata_get(bucketName,objectName,key,mongo)
        if jsonData:
            return jsonData
        else:
            abort(404)
    elif request.args.get('metadata') == "" and len(request.args) == 1:
        jsonData = metadata_get_all(bucketName,objectName,mongo)
        if jsonData:
            return jsonData
        else:
            abort(404)
    elif len(request.args) == 0:
        Range = request.headers.get("Range")
        if Range is None:
            Range = "bytes=0-"
        Range = Range.split("=")[1]
        Range = Range.split("-")
        dl = prepare_download(bucketName,objectName,Range[0],Range[1],mongo)
        # return str(validate_download_range(Range[0],Range[1],39))
        if dl:
            path = bucketName + "/" + objectName + "/"
            rv = Response(object_generator(path,dl[0],dl[1],dl[2][0],dl[3][0],dl[2][1],dl[3][1]),200,direct_passthrough=True)
            rv.headers["eTag"] = get_eTag(bucketName,objectName,mongo)
            rv.headers["Content-Type"] = "image/gif"
            return rv
        else:
            abort(404)

@app.route('/validate/<bucketName>/<objectName>',methods = ['GET'])
def validate(bucketName,objectName):
    authorize = validate_object(bucketName,objectName,mongo)
    if authorize:
        return "success"
    abort(404)

if __name__=='__main__':
    app.run(host='0.0.0.0')    