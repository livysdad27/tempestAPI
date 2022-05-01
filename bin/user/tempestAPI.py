from turtle import clear
import websocket
import _thread
import time
import rel
import json

personal_token = 'eba0c0f1-39d7-4321-bc63-f1c348dbf757'
tempest_device_ID = '195926'
tempest_station_ID = '72866'
tempest_endpoint='wss://ws.weatherflow.com/swd/data'
websocket_uri=tempest_endpoint + '?api_key=' + personal_token

def on_message(ws, message):
    print('=========================================')
    msg = json.loads(message)
    if 'obs' in msg.keys():
      print(msg['obs'])
    else:
        print(json.dumps(msg, indent=4))
    print('=========================================')


def on_error(ws, error):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(error)
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

def on_close(ws, close_status_code, close_msg):
    print('-------------------------------------')
    print("### closed ###")
    print('-------------------------------------')

def on_open(ws):
    print("Opened connection")
    ws.send(('{"type":"listen_start", "device_id":' + tempest_device_ID + ',' + ' "id":"corrOpenOb"}'))
    ws.send(('{"type":"listen_rapid_start", "device_id":' + tempest_device_ID + ',' + ' "id":"corrOpenWind"}'))
    ws.send(('{"type":"listen_start_events", "station_id":' + tempest_station_ID + ',' + ' "id":"corrOpenStation"}')) 


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(websocket_uri,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
