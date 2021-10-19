import time
from time import gmtime, strftime

from datetime import datetime,timezone

import requests
import json
from azure.eventhub import EventHubProducerClient, EventData
import os
os.environ["CONNECTION_STRING"] = "Endpoint=sb://pythoneventhb.servicebus.windows.net/;SharedAccessKeyName=eventpolicy;SharedAccessKey=gR5uUifVoEXQpY57GvQMvZ/YUpAqA87A/hSo3JgdgC8=;EntityPath=eventhub"

from random import randint



from serial import Serial

from pyshimmer import ShimmerBluetooth, DEFAULT_BAUDRATE, DataPacket, EChannelType

eventhub_name = 'eventhub'
client = EventHubProducerClient.from_connection_string(os.environ.get('CONNECTION_STRING'), eventhub_name=eventhub_name)
Session_ID = "002"+ date_time_unix
def send_as_json(stream):
    
    event_data_batch = client.create_batch()
    date_time =  datetime.fromtimestamp(float(sample.split()[1])).isoformat(sep=' ', timespec='milliseconds')
    date_time_unix = str(time.time())
    sample_json1 = {"stream_type" : "EChannelType.ACCEL_LN_X", "Value" : str(stream[EChannelType.ACCEL_LN_X]), "dateTime" : date_time, "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    sample_json2 = {"stream_type" : "EChannelType.ACCEL_LN_Y", "Value" : str(stream[EChannelType.ACCEL_LN_Y]), "dateTime" : date_time, "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    sample_json3 = {"stream_type" : "EChannelType.ACCEL_LN_Z", "Value" : str(stream[EChannelType.ACCEL_LN_Z]), "dateTime" : date_time, "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    sample_json4 = {"stream_type" : "EChannelType.VBATT", "Value" : str(stream[EChannelType.VBATT]), "dateTime" : date_time, "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    sample_json5 = {"stream_type" : "EChannelType.GYRO_MPU9150_X", "Value" : str(stream[EChannelType.GYRO_MPU9150_X]), "dateTime" : date_time, "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    sample_json6 = {"stream_type" : "EChannelType.GYRO_MPU9150_Y", "Value" : str(stream[EChannelType.GYRO_MPU9150_Y]), "dateTime" : date_time, "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    sample_json7 = {"stream_type" : "EChannelType.GYRO_MPU9150_Z", "Value" : str(stream[EChannelType.GYRO_MPU9150_Z]), "dateTime" : datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    sample_json8 = {"stream_type" : "EChannelType.MAG_LSM303DLHC_X", "Value" : str(stream[EChannelType.MAG_LSM303DLHC_X]), "dateTime" : date_time, "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    sample_json9 = {"stream_type" : "EChannelType.MAG_LSM303DLHC_Y", "Value" : str(stream[EChannelType.MAG_LSM303DLHC_Y]), "dateTime" : date_time, "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    sample_json10 = {"stream_type" : "EChannelType.MAG_LSM303DLHC_Z", "Value" : str(stream[EChannelType.MAG_LSM303DLHC_Z]), "dateTime" : date_time, "dateTime_Unix" : date_time_unix, "Session_ID" : Session_ID, "Participant" : "Rishav Kumar", "Participant_ID" : "002"}
    event_data_batch.add(EventData(json.dumps(sample_json1)))
    event_data_batch.add(EventData(json.dumps(sample_json2)))
    event_data_batch.add(EventData(json.dumps(sample_json3)))
    event_data_batch.add(EventData(json.dumps(sample_json4)))
    event_data_batch.add(EventData(json.dumps(sample_json5)))
    event_data_batch.add(EventData(json.dumps(sample_json6)))
    event_data_batch.add(EventData(json.dumps(sample_json7)))
    event_data_batch.add(EventData(json.dumps(sample_json8)))
    event_data_batch.add(EventData(json.dumps(sample_json9)))
    event_data_batch.add(EventData(json.dumps(sample_json10)))
    client.send_batch(event_data_batch)




def handler(pkt: DataPacket) -> None:
    send_as_json(pkt._values)
    


if __name__ == '__main__':
    serial = Serial('/dev/rfcomm1', DEFAULT_BAUDRATE)
    shim_dev = ShimmerBluetooth(serial)

    shim_dev.initialize()

    dev_name = shim_dev.get_device_name()
    print(f'My name is: {dev_name}')

    shim_dev.add_stream_callback(handler)

    shim_dev.start_streaming()
    
    while True:
        time.sleep(1)
