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
    if validate_bucket(bucketName,mongo):
        bucket = mongo.db[bucketName]
        return bucket.find_one({"_id":object})

def validate_download_range(start,end,length):
    if start.isdigit():
        if int(start) < length and end == "":
            DOWNLOAD_ABLE = True # to the end of file
        if end.isdigit() and int(end) < length and int(start) <= int(end):
            DOWNLOAD_ABLE = True
        else:
            DOWNLOAD_ABLE = False #to some point
    else:
        DOWNLOAD_ABLE = False

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
        
def prepare_download(bucketName,objectName,strartb,endb):
    if validate_bucket(bucketName,mongo):
        obj = validate_object(bucketName,objectName,mongo)
        if obj:
            objlen = obj["length"] 
            validate_download_range(startb,endb,objlen)
            if DOWNLOAD_ABLE:
                listFile = obj["part_data"].keys()
                sorted(listFile)
                rangeList = [int(obj["part_data"][f][1]) for f in listFile]
                start = seek_part(strartb,rangeList)
                end = seek_part(endb,listFile)
                return listFile,start,end
            # if DOWNLOAD_MODE == 1:
                
            # if DOWNLOAD_MODE == 2:
                 
            
    return False 



        

