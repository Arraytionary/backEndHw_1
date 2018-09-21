from flask import Flask, url_for,request,jsonify,abort
from flask_pymongo import PyMongo
from werkzeug.exceptions import BadRequest,Response
from Utils.object_utils import *
from Utils.file_utils import object_generator
from Utils.bucket_utils import *
import re,time,requests,pymongo,os,sys,hashlib,shutil


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

@app.route('/<bucket>',methods = ['POST'])
def bucket_create(bucket):
    # is_create = request.args.get('create')
        if request.args.get('create') == "":
            jsonData = createBucket(bucket)
            if(jsonData):
                return jsonData
            else: 
                raise BadRequest()

@app.route('/<bucket>',methods = ['DELETE'])
def bucket_delete(bucket):
    if request.args.get('delete') == "":
        if(delete(bucket)):
            return "yay delete %s complete" %bucket
        else:
            return BadRequest()

@app.route('/<bucket>',methods = ['GET'])
def bucket_list(bucket):
    if request.args.get('list') == "":
        jsonData = listOut(bucket,mongo)
        if(jsonData):
            return jsonData
        else:
            raise BadRequest()

@app.route('/<bucketName>/<objectName>',methods = ['POST'])
def object_POST_handler(bucketName,objectName):
    if request.args.get('create') == "":
        if create_object(bucketName,objectName,mongo):
            return "success"
        else:
            raise BadRequest()

    elif request.args.get('complete') == "":
        jsonData = complete(bucketName,objectName,mongo)
        if "error" not in jsonData.json:
            return jsonData
        else:
            # raise BadRequest
            return jsonData,400

@app.route('/<bucketName>/<objectName>',methods = ['PUT'])
def object_PUT_handler(bucketName,objectName):
    if request.args.get('metadata') == "" and request.args.get('key') is not None:
        key = request.args.get('key')
        success = metadata_adder(bucketName,objectName,key,mongo)
        if success:
            return "add/update metadata successful"
        else:
            abort(404)

        #if for checking upload al part
    elif request.args.get("partNumber") is not None:
        if(int(request.args.get("partNumber")) in range(1,10001)):
            data = request.get_data()
            md5 = request.headers.get("Content-MD5")
            length = request.headers.get("Content-Length")

            jsonData = upload(data,bucketName,objectName,length,md5,int(request.args.get("partNumber")),mongo)
            if "error" not in jsonData.json:
                return jsonData
            else:
                # raise BadRequest
                return json,400
        else:
            # raise BadRequest
            return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"InvalidPartNumber"}),400

@app.route('/<bucketName>/<objectName>',methods = ['DELETE'])
def object_DELETE_handler(bucketName,objectName):
    if request.args.get('metadata') == "" and request.args.get('key') is not None:
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
    if request.args.get('metadata') == "" and request.args.get('key') is not None:
        key = request.args.get('key')
        jsonData = metadata_get(bucketName,objectName,key,mongo)
        if jsonData:
            return jsonData
        else:
            abort(404)
    elif request.args.get('metadata') == "":
        jsonData = metadata_get_all(bucketName,objectName,mongo)
        if jsonData:
            return jsonData
        else:
            abort(404)
    else:
        Range = request.headers.get("Range")
        Range = Range.split("=")[1]
        Range = Range.split("-")
        dl = prepare_download(bucketName,objectName,Range[0],Range[1],mongo)
        # return str(validate_download_range(Range[0],Range[1],39))
        if dl:
            path = bucketName + "/" + objectName + "/"
            rv = Response(object_generator(path,dl[0],dl[1],dl[2][0],dl[3][0],dl[2][1],dl[3][1]),200,direct_passthrough=True)
            # rv.headers["eTag"] = get_eTag(bucketName,objectName,mongo)
            return rv
        else:
            abort(404)

# def create_object(bucketName,object):
#     bucket = mongo.db.buckets
#     if bucket.find_one({"_id":bucketName}):
#         bucket = mongo.db[bucketName]

#         exist = bucket.find_one({"_id":object})
#         if(not exist):
#             timeStamp = int(time.time())
#             bucket.insert_one({"_id":object,"complete":False,"part_data":dict(),"created":timeStamp,"modified":timeStamp,"metadata":dict()})
#             path = bucketName+"/"+object
#             if not os.path.exists(path):
#                 os.makedirs(path)
#             # do a bunch more thingssssssss
#             return True
#     return False

# def upload(data,bucketName,object,length,md5,partNum):
#     bucket = mongo.db.buckets
#     if bucket.find_one({"_id":bucketName}):
#         bucket = mongo.db[bucketName]
#         exist = bucket.find_one({"_id":object})
#         if(exist):
#             if not exist["complete"]:
#                 objectData = request.data
#                 m = hashlib.md5()
#                 m.update(objectData)
#                 if m.hexdigest() == md5:
#                     if str(len(objectData)) == length:
#                         file_name = object + "_part"+str(format(partNum,"05"))
#                         path = bucketName + "/" + object + "/" + file_name
#                         with open(path,"wb") as fo:
#                             fo.write(objectData)
#                         fo.close()
#                         os.chmod(path,0o644)
#                         if not exist["complete"]:
#                             exist["part_data"][file_name] = [m.digest(),length]
#                             timeStamp = int(time.time())
#                             exist["modified"] = timeStamp
#                             bucket.save(exist)
#                             return jsonify({"md5":md5,'length':length,"partNumber":partNum})
#                         #ask aj about permission
#                         else:
#                             return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"UploadAlreadyComplete"}) 
#                     else:
#                         return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"LengthMismatched"}) 
#                 else:
#                     return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"MD5Mismatched"})
#             else:
#                 return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"ObjectAlreadyExist"})
#         else:
#             return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"InvalidObjectName"})
#     else:
#         return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"InvalidBucket"}) 

# def complete(bucketName,object):
#     bucket = mongo.db.buckets
#     if bucket.find_one({"_id":bucketName}):
#         bucket = mongo.db[bucketName]
#         obj = bucket.find_one({"_id":object})
#         if obj and not obj["complete"] :
#             # this is for list from file in folder
#             # listFile = os.listdir(bucketName+"/"+object+"/")
#             listFile = obj["part_data"].keys()
#             sorted(listFile)
            
#             part = 0
#             # temp = ""
#             md5 = b''
#             length = 0
#             if len(listFile) == 0:
#                 return jsonify({"eTag":"","length":length,"name":object}) 
#             for file in listFile:
                
#                 # get byte md5
#                 md5 += obj["part_data"][file][0]
#                 length += int(obj["part_data"][file][1])
#                 part += 1

#             m = hashlib.md5()
#             m.update(md5)
#             md5 = m.hexdigest()
#             eTag = md5+"-"+str(part)
#             obj["complete"] = True
#             obj["eTag"] = eTag
#             obj["length"] = length
#             timeStamp = int(time.time())
#             obj["modified"] = timeStamp
#             bucket.save(obj)
#             return jsonify({"eTag":eTag,"length":length,"name":object})    
                    
#         else:
#             return jsonify({"eTag":"","length":0,"name":object,"error":"InvalidObjectName"})
#     else:
#         return jsonify({"eTag":"","length":0,"name":object,"error":"InvalidBucket"})

# def delete_object_by_part(bucketName,object,partNum):
#     bucket = mongo.db.buckets
#     if bucket.find_one({"_id":bucketName}):
#         bucket = mongo.db[bucketName]

#         obj = bucket.find_one({"_id":object})
#         key = object+"_part"+str(format(partNum,"05"))
#         if obj:
#             if not obj["complete"]:
#                 if key in obj["part_data"].keys():
#                     del obj["part_data"][key]
#                     bucket.save(obj)
#                     return True
#     return False

# def delete_object(bucketName,object):
#     bucket = mongo.db.buckets
#     if bucket.find_one({"_id":bucketName}):
#         bucket = mongo.db[bucketName]
#         obj = bucket.find_one({"_id":object})
#         if obj:
#             bucket.remove(obj)
#             return True
#     return False

if __name__=='__main__':
    app.run(debug=True)    