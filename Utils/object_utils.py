from flask import stream_with_context, request, Response
import re,time,requests,pymongo,os,sys,hashlib,shutil

DOWNLOAD_ABLE = False

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
            DOWNLOAD_ABLE = True # to the end of file
            return True
        elif end.isdigit() and int(end) < length and int(start) <= int(end):
            DOWNLOAD_ABLE = True
            return True
        else:
            DOWNLOAD_ABLE = False #to some point
            return False
    else:
        DOWNLOAD_ABLE = False
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
                end = seek_part(int(endb),rangeList)
                return listFile,rangeList,start,end
            # if DOWNLOAD_MODE == 1:
                
            # if DOWNLOAD_MODE == 2:
                 
            
    return False 



        

