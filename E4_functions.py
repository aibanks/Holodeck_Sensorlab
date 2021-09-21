import sys
import socket
import time
from datetime import datetime 
import requests
import json
#from azure.eventhub import EventHubProducerClient, EventData
import os
import time
from random import randint

#participant = input("Participant's Full Name: ")
#participant_ID = input("Participant ID: ")
participant = "Tony Banks"
participant_ID = "001"
startTime = time.time()
session_ID = participant_ID +"_" + str(startTime)

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

def stream():
    response = s.recv(bufferSize).decode("utf-8")
    print(response)
    #print('Data streaming in progress')
    if "connection lost to device" in response:
        print(response.decode("utf-8"))
        reconnect()
    #samples = response.split("\r\n")
    #print(samples)

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