import requests as rq
import time
import json
import weewx.drivers
import weewx.units
import weewx.wxformulas
import weedb
import weeutil.weeutil
import syslog
import getopt

DRIVER_VERSION = "0.7"
HARDWARE_NAME = "Weatherflow Tempest"
DRIVER_NAME = "tempestAPI"

def loader(config_dict, engine):
    return tempestAPI(**config_dict[DRIVER_NAME])

def logmsg(level, msg):
    syslog.syslog(level, 'tempestAPI: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class tempestAPI(weewx.drivers.AbstractDevice):
    def __init__(self, **cfg_dict):
        self._personal_token = str(cfg_dict.get('personal_token'))
        self._tempest_device_id = str(cfg_dict.get('tempest_device_id'))
        self._tempest_station_id = str(cfg_dict.get('tempest_station_id'))
        self._tempest_rest_endpoint = str(cfg_dict.get('tempest_rest_endpoint'))
        self._rest_uri=self._tempest_rest_endpoint + self._tempest_device_id + '?api_key=' + self._personal_token

    def hardware_name(self):
        return HARDWARE_NAME

    def genLoopPackets(self):
        last_timestamp = 10
        while True:
            loop_packet = {}
            mqtt_data = []
            resp = rq.get(self._rest_uri)
            time.sleep(5)
            if resp.status_code == 200:
                mqtt_data = resp.json()['obs'][0]
                if last_timestamp != mqtt_data[0]:
                    last_timestamp = mqtt_data[0]
                    loop_packet['dateTime'] = mqtt_data[0]
                    loop_packet['usUnits'] = weewx.METRICWX
                    loop_packet['outTemp'] = mqtt_data[7]
                    loop_packet['outHumidity'] = mqtt_data[8]
                    loop_packet['pressure'] = mqtt_data[6]
                    loop_packet['supplyVoltage'] = mqtt_data[16]
                    loop_packet['radiation'] = mqtt_data[11]
                    loop_packet['rain'] = mqtt_data[19]
                    loop_packet['UV'] = mqtt_data[10]
                    loop_packet['lightening_distance'] = mqtt_data[14]
                    loop_packet['lightening_strike_count'] = mqtt_data[15]

                    if loop_packet != {}:
                        try:
                            yield loop_packet
                        except:
                            logerr('Could not submit loop packet' + str(loop_packet))
            
            else:
                logerr("Attempt to connect to Tempest API at " + self._tempest_rest_endpoint + "failed with status " + resp.status_code)