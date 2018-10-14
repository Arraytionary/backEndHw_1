from .object_utils import *
from flask import jsonify
def createBucket(bucketName,mongo):
    def add_bucket(bucketName,timeStamp,mongo):
        bucket = mongo.db.buckets
        #Try to create new bucket with a unique bucket name
        try:
            bucket.insert_one({'_id' : bucketName,'created' : timeStamp,'modified':timeStamp})
            path = "sos/" + bucketName   
            if not os.path.exists(path):    #create folder if not exist
                os.makedirs(path)
            return True
        #Bucket's name already exist in the db
        except pymongo.errors.DuplicateKeyError:
            return False

    timeStamp = int(time.time())
    if(add_bucket(bucketName,timeStamp,mongo)):
        return jsonify({"created":timeStamp,"modified":timeStamp,"name":bucketName})

def delete(bucketName,mongo):
    bucket = mongo.db.buckets
    result = bucket.find_one({"_id":bucketName})
    if result :
        bucket.remove(result)
        if mongo.db[bucketName]:
            mongo.db[bucketName].drop()

        # This is for really delete file in the future
        # path = bucketName
        # if os.path.exists(path):
        #     shutil.rmtree(path)
        return True
    else:
        return False

def list_bucket(mongo):
    buckets = mongo.db.buckets.find()
    all_buckets = []
    for b in buckets:
        all_buckets.append(b["_id"])
    return jsonify({"buckets":all_buckets})

def listOut(bucketName,mongo):
    if validate_bucket(bucketName,mongo):
        bucket = mongo.db.buckets.find_one({"_id":bucketName})
        objectList = mongo.db[bucketName].find()
        objects = []
        for n in objectList:
            if n["complete"]:
                t = {}
                t["name"] = n["_id"]
                t["eTag"] = n["eTag"]
                t["created"] = n["created"]
                t["modified"] = n["modified"]
                objects.append(t)
        return jsonify({"created":bucket["created"],"modified":bucket["modified"],"name":bucket["_id"],"objects":objects})
    return False