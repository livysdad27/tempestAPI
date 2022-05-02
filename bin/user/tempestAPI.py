import websocket
import _thread
import time
import rel
import json

personal_token = ''
tempest_device_ID = '195926'
tempest_station_ID = '72866'
tempest_endpoint='wss://ws.weatherflow.com/swd/data'
websocket_uri=tempest_endpoint + '?api_key=' + personal_token

def on_message(ws, message):
    loop_packet = {}
    mqtt_data = []
    print('=========================================')
    msg = json.loads(message)
    if msg['type']=='obs_st':
        mqtt_data = msg['obs'][0]
        loop_packet['dateTime'] = mqtt_data[0]
        loop_packet['usUnits'] = 16
        loop_packet['outTemp'] = mqtt_data[7]
        loop_packet['outHumidity'] = mqtt_data[8]
        loop_packet['pressure'] = mqtt_data[6]
        loop_packet['supplyVoltage'] = mqtt_data[16]
        loop_packet['radiation'] = mqtt_data[11]
        loop_packet['rain'] = mqtt_data[19]
        loop_packet['UV'] = mqtt_data[10]
        loop_packet['lightening_distance'] = mqtt_data[14]
        loop_packet['lightening_strike_count'] = mqtt_data[15]
    elif msg['type']=='rapid_wind':
        mqtt_data = msg['ob']
        loop_packet['dateTime'] = mqtt_data[0]
        loop_packet['usUnits'] = 16
        loop_packet['windSpeed'] = mqtt_data[1]
        loop_packet['windDir'] = mqtt_data[2] 
    elif msg['type']=='ack':
        print(msg['id'])
    else:
        print(json.dumps(msg, indent=4))
    if loop_packet != {}:
        print(loop_packet)
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
