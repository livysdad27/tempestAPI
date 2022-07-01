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
    syslog.syslog(level, 'tempestAPI: %s' % msg))

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
        loop_packet = {}
        mqtt_data = []
        resp = rq.get(self._rest_uri)
        if resp.status_code == 200:
            loginf("Successfull connection to Tempest REST API Endpoint")
            mqtt_data = resp.json()['obs'][0]
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
            loginf("Generated a loop packet")
            time.sleep(5)

        if loop_packet != {}:
            loginf("submitting loop packet")
            try:
                yield loop_packet
                loginf('Successfully submitted loop packet FLAG')
            except:
                logerr('Could not submit loop packet')