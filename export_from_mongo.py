import pymongo
import pandas
import json
from pymongo import MongoClient

Client_Mongo_new=MongoClient()

db=Client_Mongo_new.Sensorlab
c=db.test_nestedJSON

cursor=c.find()
docs=list(cursor)  #retrieves exported MongoDB data from database.

for i in range(len(docs)):
    docs[i]['_id'] = str(docs[i]['_id'])

data = {'info':docs}

jsonFile = open("data.json", "w")
jsonFile.write(json.dumps(data))
jsonFile.close()
