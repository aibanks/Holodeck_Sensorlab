import sys
import socket
import time
from datetime import datetime 
import requests
import json
from azure.eventhub import EventHubProducerClient, EventData
import os
import time
from random import randint

#participant = input("Participant's Full Name: ")
#participant_ID = input("Participant ID: ")
#participant = "Tony Banks"    # need to generalize
#participant_ID = "001"         # need to generalize
#startTime = time.time()
#session_ID = participant_ID +"_" + str(startTime)

# SELECT DATA TO STREAM
acc = True      # 3-axis acceleration
bvp = True     # Blood Volume Pulse
gsr = True      # Galvanic Skin Response (Electrodermal Activity)
tmp = True      # Temperature
ibi = True      # Interbeat Interval and Heartbeat
bat = True      # Device Battery
tag = True     # Tag taken from the device (by pressing the button)

serverAddress = '127.0.0.1'
serverPort = 28000
bufferSize = 4096

#deviceID = 'CDCB11' # 'A03003'

def connect(deviceID):
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
    connection_response = s.recv(bufferSize)
    connection_response = connection_response.decode("utf-8")
    print(connection_response)

    print("Pausing data receiving")
    s.send("pause ON\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))

    return connection_response
#connect()

#time.sleep(1)

def subscribe_to_data():
    global acc, bvp, gsr, tmp, ibi, bat, tag
    if acc:
        print("Subscribing to ACC")
        s.send(("device_subscribe " + 'acc' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bvp:
        print("Subscribing to BVP")
        s.send(("device_subscribe " + 'bvp' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if gsr:
        print("Subscribing to GSR")
        s.send(("device_subscribe " + 'gsr' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tmp:
        print("Subscribing to Temp")
        s.send(("device_subscribe " + 'tmp' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if ibi:
        print("Subscribing to IBI")
        s.send(("device_subscribe " + 'ibi' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bat:
        print("Suscribing to Batt")
        s.send(("device_subscribe " + 'bat' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tag:
        print("Subscribing to Tag")
        s.send(("device_subscribe " + 'tag' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))

    print("Resuming data receiving")
    s.send("pause OFF\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))
#subscribe_to_data()

def disconnect():
    print("Disconnecting device")
    s.send("device_disconnect\r\n".encode())

def reconnect():
    print("Reconnecting...")
    connect()
    subscribe_to_data()  

def convert_to_json(sample, participant, participant_ID, session_ID):
    stream_type = sample.split()[0]
    if stream_type == "E4_Acc":
        new_timestamp = datetime.fromtimestamp(float(sample.split()[1])).isoformat(sep=' ', timespec='milliseconds') #recent update to include milliseconds
        new_timestamp_unix = sample.split()[1] #recent update to include unix timestamp to make querying easier
        new_data = [int(sample.split()[2].replace(',','.')), int(sample.split()[3].replace(',','.')), int(sample.split()[4].replace(',','.'))]
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


def stream(participant, participant_ID, session_ID):
    response = s.recv(bufferSize).decode("utf-8")
    print(response)
    #print('Data streaming in progress')
    if "connection lost to device" in response:
        print(response.decode("utf-8"))
        reconnect()
    #samples = response.split("\r\n")
    #print(samples)
    event_data_batch = client.create_batch()
    samples = response.split("\r\n")
    for sample in samples:
        if sample[0:2] == "E4":
            sample_json = convert_to_json(sample, participant, participant_ID, session_ID)
            print(sample_json)
            event_data_batch.add(EventData(sample_json))
    client.send_batch(event_data_batch)
    #print("Data streaming in progress")

def unsubscribe_to_data():
    global acc, bvp, gsr, tmp, ibi, bat, tag
    if acc:
        print("Unsubscribing to ACC")
        s.send(("device_subscribe " + 'acc' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bvp:
        print("Unsubscribing to BVP")
        s.send(("device_subscribe " + 'bvp' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if gsr:
        print("Unsubscribing to GSR")
        s.send(("device_subscribe " + 'gsr' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tmp:
        print("Unsubscribing to Temp")
        s.send(("device_subscribe " + 'tmp' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if ibi:
        print("Unsubscribing to IBI")
        s.send(("device_subscribe " + 'ibi' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bat:
        print("Unsubscribing to Batt")
        s.send(("device_subscribe " + 'bat' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tag:
        print("Unsubscribing to Tag")
        s.send(("device_subscribe " + 'tag' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))