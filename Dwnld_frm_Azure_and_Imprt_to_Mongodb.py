import time
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobServiceClient
import json
import os
from pymongo import MongoClient

# Define function to build nested json 
def make_nested_json(list_of_json):
    sessions = [
        {
            'Session_ID': list_of_json[0]['Session_ID'],
            'Participant_ID': list_of_json[0]['Participant_ID'],
            'Participant': list_of_json[0]['Participant'],
            'Streams' : [
                {
                    'stream_type': list_of_json[0]['stream_type'],
                    'data': []
                }
            ]
        }
    ]
    
    for i in range(len(list_of_json)):
        sessions_in_dict = [a_dict["Session_ID"] for a_dict in sessions]
        indexed_sessionID = list_of_json[i]['Session_ID']
        indexed_stream_type = list_of_json[i]['stream_type']
        if indexed_sessionID in sessions_in_dict:
            pass
        else:
            sessions.append(
                {
                    'Session_ID': indexed_sessionID,
                    'Participant_ID': list_of_json[i]['Participant_ID'],
                    'Participant': list_of_json[i]['Participant'],
                    'Streams': [
                        {
                            'stream_type': indexed_stream_type,
                            'data': []
                        }
                    ]
                }
            )
        sessions_in_dict = [a_dict["Session_ID"] for a_dict in sessions]
        n_session = sessions_in_dict.index(indexed_sessionID)
        streams_in_session = [a_dict["stream_type"] for a_dict in sessions[n_session]['Streams']]
        if indexed_stream_type in streams_in_session:
            pass
        else:
            sessions[n_session]['Streams'].append(
                {
                    'stream_type': indexed_stream_type,
                    'data': []
                }
            )
        streams_in_session = [a_dict["stream_type"] for a_dict in sessions[n_session]['Streams']]
        n_stream = streams_in_session.index(indexed_stream_type)
        sessions[n_session]['Streams'][n_stream]['data'].append(
            {
                'Value': list_of_json[i]['Value'],
                'dateTime': list_of_json[i]['dateTime_Unix']
            }
        )
    
    return sessions

blob_service_client_instance = BlobServiceClient(account_url="https://uaholodecksensorlab.blob.core.windows.net",credential="GX+Fn1hVo3RDWRGuCxMAVDVFA/maCM2NdGx4Kffv4tWnG6DU8C1NOVH5Rv694e3HVNCmlinkeAKMgnXBvsr7nA==")
container = ContainerClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=uaholodecksensorlab;AccountKey=GX+Fn1hVo3RDWRGuCxMAVDVFA/maCM2NdGx4Kffv4tWnG6DU8C1NOVH5Rv694e3HVNCmlinkeAKMgnXBvsr7nA==;EndpointSuffix=core.windows.net", container_name="container2")

new_files = []
all_files = []

blob_list = container.list_blobs()
for blob in blob_list:
    print(blob.name + '\n')
    all_files.append(blob.name)
    if blob.name not in os.listdir(os.curdir):
        new_files.append(blob.name)
        t1=time.time()
        blob_client_instance = blob_service_client_instance.get_blob_client("container2", blob.name, snapshot=None)
        with open(blob.name, "wb") as my_blob:
            blob_data = blob_client_instance.download_blob()
            blob_data.readinto(my_blob)
        t2=time.time()
        print(("It takes %s seconds to download "+blob.name + '\n') % (t2 - t1))

### Import new data to mongodb, one file at a time
# Making Connection
myclient = MongoClient("mongodb://localhost:27017/")
# database
db = myclient["Sensorlab"]  #update here to switch database
# Create or switch to collection
Collection = db["test_nestedJSON"]  #update here to switch collection
for i in range(len(new_files)):
    with open(new_files[i]) as f:
        content = f.readlines()
    file_data = []
    for data in content:
        file_data.append(json.loads(data))

    nested_json_file_data = make_nested_json(file_data)

    if isinstance(nested_json_file_data, list):
        Collection.insert_many(nested_json_file_data)
    else:
        Collection.insert_one(nested_json_file_data)

    print(f"Imported {new_files[i]} to the database.")
