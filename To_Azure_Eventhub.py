## Successful to recieve data from E4 and simultaneously push it to Azure

import socket
import time
from datetime import datetime 
import requests
import json
from azure.eventhub import EventHubProducerClient, EventData
import os
import time

from random import randint
#%matplotlib qt
#%matplotlib inline

participant = input("Participant's Full Name: ")
participant_ID = input("Participant ID: ")
startTime = time.time()
session_ID = participant_ID +"_" + str(startTime)

# SELECT DATA TO STREAM
acc = True      # 3-axis acceleration
bvp = True     # Blood Volume Pulse
gsr = True      # Galvanic Skin Response (Electrodermal Activity)
tmp = True      # Temperature
ibi = True      # Interbeat Interval and Heartbeat
bat = False      # Device Battery
tag = False     # Tag taken from the device (by pressing the button)

serverAddress = '127.0.0.1'
serverPort = 28000
bufferSize = 4096

deviceID = 'CDCB11' # 'A03003'

def connect():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)

    print("Connecting to server")
    s.connect((serverAddress, serverPort))
    print("Connected to server\n")

    print("Devices available:")
    s.send("device_list\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))

    print("Connecting to device")
    s.send(("device_connect " + deviceID + "\r\n").encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))

    print("Pausing data receiving")
    s.send("pause ON\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))
connect()

time.sleep(1)

def suscribe_to_data():
    if acc:
        print("Suscribing to ACC")
        s.send(("device_subscribe " + 'acc' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bvp:
        print("Suscribing to BVP")
        s.send(("device_subscribe " + 'bvp' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if gsr:
        print("Suscribing to GSR")
        s.send(("device_subscribe " + 'gsr' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tmp:
        print("Suscribing to Temp")
        s.send(("device_subscribe " + 'tmp' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if ibi:
        print("Suscribing to IBI")
        s.send(("device_subscribe " + 'ibi' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bat:
        print("Suscribing to Batt")
        s.send(("device_subscribe " + 'bat' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tag:
        print("Suscribing to Tag")
        s.send(("device_subscribe " + 'tag' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))

    print("Resuming data receiving")
    s.send("pause OFF\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))
suscribe_to_data()

time.sleep(1)

def reconnect():
    print("Reconnecting...")
    connect()
    suscribe_to_data()
    #stream()

def disconnect():
    s.send("device_disconnect\r\n".encode())

def convert_to_json(sample):
    stream_type = sample.split()[0]
    if stream_type == "E4_Acc":
        new_timestamp = datetime.fromtimestamp(float(sample.split()[1])).isoformat(sep=' ', timespec='milliseconds') #recent update to include milliseconds
        new_timestamp_unix = sample.split()[1] #recent update to include unix timestamp to make querying easier
        new_data = [int(samples[i].split()[2].replace(',','.')), int(samples[i].split()[3].replace(',','.')), int(samples[i].split()[4].replace(',','.'))]
        sample_jsonX = {"stream_type" : "E4_Acc_X", "Value" : new_data[0], "dateTime" : new_timestamp, "dateTime_Unix" : new_timestamp_unix, "Session_ID" : session_ID, "Participant" : participant, "Participant_ID" : participant_ID}
        sample_jsonY = {"stream_type" : "E4_Acc_Y", "Value" : new_data[1], "dateTime" : new_timestamp, "dateTime_Unix" : new_timestamp_unix, "Session_ID" : session_ID, "Participant" : participant, "Participant_ID" : participant_ID}
        sample_jsonZ = {"stream_type" : "E4_Acc_Z", "Value" : new_data[2], "dateTime" : new_timestamp, "dateTime_Unix" : new_timestamp_unix, "Session_ID" : session_ID, "Participant" : participant, "Participant_ID" : participant_ID}
        sample_json = [sample_jsonX, sample_jsonY, sample_jsonZ]
        sample_json = json.dumps(sample_json)    #might have issues from trying to batch more than 1 json at a time later in the code
    else:
        new_timestamp = datetime.fromtimestamp(float(sample.split()[1])).isoformat(sep=' ', timespec='milliseconds') #recent update to include milliseconds
        new_timestamp_unix = sample.split()[1] #recent update to include unix timestamp to make querying easier
        new_data = float(sample.split()[2])
        sample_json = {"stream_type" : stream_type, "Value" : new_data, "dateTime" : new_timestamp, "dateTime_Unix" : new_timestamp_unix, "Session_ID" : session_ID, "Participant" : participant, "Participant_ID" : participant_ID}
        sample_json = json.dumps(sample_json)
    return(sample_json)

eventhub_name = 'eventhub'
client = EventHubProducerClient.from_connection_string(os.environ.get('AZURE_EVENTHUB_CONNECTION_STRING'), eventhub_name=eventhub_name)

try:
    while True:
        response = s.recv(bufferSize).decode("utf-8")
        #print(response)
        if "connection lost to device" in response:
            print(response.decode("utf-8"))
            reconnect()
        event_data_batch = client.create_batch()
        samples = response.split("\r\n")
        for i in range(len(samples)-1):
            sample_json = convert_to_json(samples[i])
            #print(sample_json)
            event_data_batch.add(EventData(sample_json))
        client.send_batch(event_data_batch)
        print("Data streaming in progress")
except KeyboardInterrupt:
    print('interrupted!')
    disconnect()