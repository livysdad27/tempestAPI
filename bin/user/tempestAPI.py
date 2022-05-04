import websocket
import _thread
import time
import rel
import json
import weewx
import getopt

DRIVER_VERSION = "0.8"
HARDWARE_NAME = "Weatherflow Tempest"
DRIVER_NAME = "tempestAPI"

def loader(config_dict, engine):
    return tempestAPI(**config_dict[DRIVER_NAME])

def logmsg(level, msg):
    syslog.syslog(level, 'tempestAPI: %s: %s' %
                  (threading.currentThread().getName(), msg))

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)


class tempestAPI(weewx.drivers.AbstractDevice):

    def __init__(self, **cfg_dict):
        self._personal_token = str(cfg_dict.get('personal_token'))
        self._tempest_device_ID = str(cfg_dict.get('tempest_device_ID'))
        self._tempest_station_ID = str(cfg_dict.get('tempest_station_ID'))
        self._tempest_websocket_endpoint = str(cfg_dict.get('weatherflow_websocket_URI'))

    def on_message(self, ws, message):
        loop_packet = {}
        mqtt_data = []
        msg = json.loads(message)
        if msg['type']=='obs_st':
            mqtt_data = msg['obs'][0]
            loop_packet['dateTime'] = mqtt_data[0]
            loop_packet['usUnits'] = weewx.METRIXWX
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
            loop_packet['usUnits'] = weewx.METRIXWX
            loop_packet['windSpeed'] = mqtt_data[1]
            loop_packet['windDir'] = mqtt_data[2] 
        #elif msg['type']=='ack':
        #    print('ACK-> ' + msg['id'])
        #else:
        #    print(json.dumps(msg))
        if loop_packet != {}:
            print(loop_packet)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print('!!!! Connection Closed !!!!')

    def on_open(self, ws):
        ws.send(('{"type":"listen_start", "device_id":' + self._tempest_device_ID + ',' + ' "id":"listen_start"}'))
        ws.send(('{"type":"listen_rapid_start", "device_id":' + self._tempest_device_ID + ',' + ' "id":"rapid_wind"}'))
        #ws.send(('{"type":"listen_start_events", "station_id":' + self._tempest_station_ID + ',' + ' "id":"listen_start_events"}')) 

    def hardware_name(self):
        return HARDWARE_NAME
    
    def genLoopPackets(self):
        websocket_uri=self._tempest_websocket_endpoint + '?api_key=' + self._personal_token
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(websocket_uri,
                                on_open=self.on_open,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                on_close=self.on_close)

        ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()
