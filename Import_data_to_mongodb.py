# Successfully adds functionality for multiple sessionIDs per json &
# reformats the json file with nested json objects to reduce redundancy


import json
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
# Making Connection to mongodb local 
myclient = MongoClient("mongodb://localhost:27017/")
# database
database_name = "Sensorlab"
db = myclient[database_name]
# Create or switch to collection
collection_name = "test_nestedJSON"
Collection = db[collection_name]

with open('0_bc82e746ce824e44a709fff45c4500c3_1.json') as f:
    content = f.readlines()
file1 = []
for data in content:
    file1.append(json.loads(data))

nested_json_file1 = make_nested_json(file1)

if isinstance(nested_json_file1, list):
    Collection.insert_many(nested_json_file1)
else:
    Collection.insert_one(nested_json_file1)

print(f'Successfully added data to mongodb.\nDatabase: {database_name}\nCollection: {collection_name}')