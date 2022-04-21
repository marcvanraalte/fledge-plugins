
import asyncio
import json
import copy
import logging

from datetime import datetime
import requests
import time

from fledge.common import logger
from fledge.plugins.north.common.common import *

__author__ = "Marc van Raalte"
__copyright__ = "Copyright (c) 2022 Alliander System Operations"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__)

_CONFIG_CATEGORY_NAME = "KTP"
_CONFIG_CATEGORY_DESCRIPTION = "KTP Full North Plugin"


_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'KTP Full north plugin',
        'type': 'string',
        'default': 'ktp_full_north',
        'readonly': 'true'
    },
    'enable': {
        'description': 'Enable ktp full plugin',
        'type': 'boolean',
        'default': 'false',
        'displayName': 'Enabled',
        'order': "3"
    },
    'url': {
        'description': 'Destination URL',
        'type': 'string',
        'default': 'https://measurement.com',
        'order': '1',
        'displayName': 'URL'
    },
    'user_id': {
        'description': 'User name',
        'type': 'string',
        'default': 'username',
        'order': '1',
        'displayName': 'User_id'
    },
    'user_pw': {
        'description': 'Password',
        'type': 'string',
        'default': 'password',
        'order': '1',
        'displayName': 'User_pw'
    },
#    'system_id': {
#        'description': 'System id',
#        'type': 'string',
#        'default': 'system_id',
#        'order': '1',
#        'displayName': 'System_id'
#    },
    'key_id': {
        'description': 'Key id',
        'type': 'string',
        'default': 'test',
        'order': '1',
        'displayName': 'Key_id'
    }
#,
#    'wma_filter': {
#        'description': 'Wma_filter to select',
#        'type': 'string',
#        'default': 'wma_filter',
#        'order': '1',
#        'displayName': 'Wma_filter'
#    }       
}


def plugin_info():
    """ Returns information about the plugin
    Args:
    Returns:
        dict: plugin information
    Raises:
    """
    return {
        'name': 'ktp_full_north',
        'version': '1.0.0',
        'type': 'north',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG 
    }


def plugin_init(config):
    handle = copy.deepcopy(config)
    return handle


async def plugin_send(handle, payload, stream_id): #is necessary otherwise unresponsive behavior #stream_id (log?) 

    system_ids = ['testsysteem1', 'testsysteem2', 'testsysteem3', 'testsysteem4', 'testsysteem5', 'testsysteem6', 'testsysteem7', 'testsysteem8', 'testsysteem9' ]
    wma_filters = ['wma_filter1', 'wma_filter2', 'wma_filter3', 'wma_filter4', 'wma_filter5', 'wma_filter6', 'wma_filter7', 'wma_filter8', 'wma_filter9']
    system_id = ""
    wma_filter = ""
    is_data_sent = False
    
    #_LOGGER.info("Test debug {}".format(payload))
    #_LOGGER.info("Test debug") # Werkt niet !!!
    
    now = datetime.now()
    f = open("/home/mvr/loggerfile.txt", "w")
    f.write("now: "+str(now)+"\n")
    f.write(str(payload)+"\n")
    
    # Set url and credentials
    measurement_url = handle['url']['value']       
    credentials = (handle['user_id']['value'], handle['user_pw']['value'])
    params = {'key': handle['key_id']['value']}
    proxies= None       
    
    num_sent = 0
    for pld in payload: 
        f.write(str(pld)+"\n")
        for wma in wma_filters:
            if wma in pld['reading'].keys():
                wma_filter = wma
                index = wma_filters.index(wma)
                system_id = system_ids[index]
                
                
        f.write(str(wma_filter)+"->"+str(system_id)+"\n")
        # Transform reading to requested format
        # Time format
        date_time_str = pld['user_ts'] 
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f%z')
        date_time_obj = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S%z")
        # Data/reading format
        new_data = []   
        new_data.append({"datetime": date_time_obj,"output": pld['reading'][wma_filter] })
        # Payload format
        new_payload = {}
        new_payload["sid"] = system_id
        new_payload["data"] = new_data        
        try:
            res = requests.post(measurement_url, params=params, json=new_payload, auth=credentials, proxies=proxies)
            time.sleep(.1)        
        except:
            is_data_sent = False
            f.write("payload not sent \n"+str(new_payload)+"\n")
        else:
            is_data_sent = True
            num_sent += 1        
                
        #time.sleep(.1) 
        #num_sent += 1
    
    f.close()
     
    #is_data_sent = True
    new_position = 0
    return is_data_sent, new_position, num_sent
    
def plugin_shutdown(config):
    pass


# TODO: North plugin can not be reconfigured? (per callback mechanism)
def plugin_reconfigure():
    pass
