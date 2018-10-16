from flask import stream_with_context, request, Response, jsonify
from mimetypes import MimeTypes
import re,time,pymongo,os,sys,hashlib,shutil


def modified_object(bucketName,objectName,mongo):
    bucket = mongo.db[bucketName]
    obj = bucket.find_one({"_id":objectName})
    timeStamp = int(time.time())
    obj["modified"] = timeStamp
    bucket.save(obj)

def validate_bucket(bucketName,mongo):
    bucket = mongo.db.buckets
    if bucket.find_one({"_id":bucketName}):
        return True
    else:
        return False
def validate_object(bucketName,objectName,mongo):
    # bucket = mongo.db.buckets
    # return bucket.find_one({"_id":bucketName})
    if validate_bucket(bucketName,mongo):
        bucket = mongo.db[bucketName]
        m = bucket.find_one({"_id":objectName})
        return m

def validate_download_range(start,end,length):
    if start.isdigit():
        if int(start) < length and end == "":
 # to the end of file
            return True
        elif end.isdigit() and int(end) < length and int(start) <= int(end):
            return True
        else:
# to some point
            return False
    else:
# invalid
        return False

def seek_part(targetByte,listFile):
    for i in range(len(listFile)):
        if targetByte - listFile[i] > 0:
            targetByte -= listFile[i]
        # elif targetByte - listFile[i] == 0:
        #     return i+1,0 # if i > len 
        else:
            if i == 0:
                return i,targetByte
            else:
                return i,targetByte - 1
        
def prepare_download(bucketName,objectName,startb,endb,mongo):
    if validate_bucket(bucketName,mongo):
        obj = validate_object(bucketName,objectName,mongo)
        if obj:
            objlen = obj["length"] 
            
            if validate_download_range(startb,endb,objlen):
                if endb == "":
                    endb = objlen
                listFile = obj["part_data"].keys()
                sorted(listFile)
                listFile = list(listFile)
                rangeList = [int(obj["part_data"][f][1]) for f in listFile]
                start = seek_part(int(startb),rangeList)
                end = seek_part(int(endb+),rangeList)
                return listFile,rangeList,start,end
    return False 

def metadata_adder(bucketName,objectName,key,request,mongo):
    obj = validate_object(bucketName,objectName,mongo)
    if obj:
        obj["metadata"][key] = request.data.decode("utf8")
        mongo.db[bucketName].save(obj)
        return True
    else:
        return False

def metadata_delete(bucketName,objectName,key,request,mongo):
    obj = validate_object(bucketName,objectName,mongo)
    if obj:
        bucket = mongo.db[bucketName]
        obj["metadata"].pop(key,None)
        bucket.save(obj)
        return True
    else:
        return False

def metadata_get(bucketName,objectName,key,mongo):
    obj = validate_object(bucketName,objectName,mongo)
    if obj:
        if key in obj["metadata"].keys():
            return jsonify({key:obj["metadata"][key]})
        else:
            return jsonify({})
    else:
        return False

def metadata_get_all(bucketName,objectName,mongo):
    obj = validate_object(bucketName,objectName,mongo)
    if obj:
        if len(obj["metadata"].keys()) > 0:
            return jsonify(obj["metadata"])
        else:
            return jsonify({})

def create_object(bucketName,objectName,mongo):
    if validate_bucket(bucketName,mongo):
        bucket = mongo.db[bucketName]

        exist = bucket.find_one({"_id":objectName})
        if(not exist):
            timeStamp = int(time.time())
            bucket.insert_one({"_id":objectName,"complete":False,"part_data":dict(),"created":timeStamp,"modified":timeStamp,"metadata":dict()})
            path = "sos/"+bucketName+"/"+objectName
            if not os.path.exists(path):
                os.makedirs(path)
            return True
    return False

def upload(data,bucketName,objectName,length,md5,partNum,mongo):
    if validate_bucket(bucketName,mongo):
        bucket = mongo.db[bucketName]
        exist = bucket.find_one({"_id":objectName})
        if(exist):
            if not exist["complete"]:
                objectData = request.data
                m = hashlib.md5()
                m.update(objectData)
                if m.hexdigest() == md5:
                    if str(len(objectData)) == length:
                        file_name = objectName + "_part"+str(format(partNum,"05"))
                        path = "sos/" + bucketName + "/" + objectName + "/" + file_name
                        with open(path,"wb") as fo:
                            fo.write(objectData)
                        fo.close()
                        os.chmod(path,0o644)
                        if not exist["complete"]:
                            exist["part_data"][file_name] = [m.digest(),length]
                            timeStamp = int(time.time())
                            exist["modified"] = timeStamp
                            bucket.save(exist)
                            return jsonify({"md5":md5,'length':length,"partNumber":partNum})
                        #ask aj about permission
                        else:
                            return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"UploadAlreadyComplete"}) 
                    else:
                        return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"LengthMismatched"}) 
                else:
                    return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"MD5Mismatched"})
            else:
                return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"ObjectAlreadyExist"})
        else:
            return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"InvalidObjectName"})
    else:
        return jsonify({"md5":md5,'length':length,"partNumber":1,"error":"InvalidBucket"}) 

def complete(bucketName,objectName,mongo):
    bucket = mongo.db.buckets
    if bucket.find_one({"_id":bucketName}):
        bucket = mongo.db[bucketName]
        obj = bucket.find_one({"_id":objectName})
        if obj and not obj["complete"] :
            listFile = obj["part_data"].keys()
            sorted(listFile)
            
            part = 0
            md5 = b''
            length = 0
            if len(listFile) == 0:
                return jsonify({"eTag":"","length":length,"name":objectName}) 
            for file in listFile:
                # get byte md5
                md5 += obj["part_data"][file][0]
                length += int(obj["part_data"][file][1])
                part += 1
            m = hashlib.md5()
            m.update(md5)
            md5 = m.hexdigest()
            eTag = md5+"-"+str(part)
            obj["complete"] = True
            obj["eTag"] = eTag
            obj["length"] = length
            timeStamp = int(time.time())
            obj["modified"] = timeStamp
            mime = MimeTypes()
            mime_type = mime.guess_type(objectName)[0]
            obj["metadata"]["Content-Type"] = mime_type
            bucket.save(obj)
            return jsonify({"eTag":eTag,"length":length,"name":objectName})    
        else:
            return jsonify({"eTag":"","length":0,"name":objectName,"error":"InvalidObjectName"})
    else:
        return jsonify({"eTag":"","length":0,"name":objectName,"error":"InvalidBucket"})

def delete_object_by_part(bucketName,objectName,partNum,mongo):
    bucket = mongo.db.buckets
    if bucket.find_one({"_id":bucketName}):
        bucket = mongo.db[bucketName]

        obj = bucket.find_one({"_id":objectName})
        key = objectName+"_part"+str(format(partNum,"05"))
        if obj:
            if not obj["complete"]:
                if key in obj["part_data"].keys():
                    del obj["part_data"][key]
                    bucket.save(obj)
                    return True
    return False

def delete_object(bucketName,objectName,mongo):
    bucket = mongo.db.buckets
    if bucket.find_one({"_id":bucketName}):
        bucket = mongo.db[bucketName]
        obj = bucket.find_one({"_id":objectName})
        if obj:
            bucket.remove(obj)
            return True
    return False

def delete_gif_object(bucketName,mongo):
    bucket = mongo.db.buckets
    if bucket.find_one({"_id":bucketName}):
        bucket = mongo.db[bucketName]
        obj = bucket.find()
        for gif in obj:
            if gif["_id"].split(".")[-1] == "gif":
                delete_object(bucketName,gif["_id"],mongo)
        return True
    return False
def get_eTag(bucketName,objectName,mongo):
    obj = validate_object(bucketName,objectName,mongo)
    if obj:
        return obj["eTag"]

        

