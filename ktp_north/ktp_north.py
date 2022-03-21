
import asyncio
import json
import copy
import logging

from datetime import datetime
import requests

from fledge.common import logger
from fledge.plugins.north.common.common import *

__author__ = "Marc van Raalte"
__copyright__ = "Copyright (c) 2022 Alliander System Operations"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__)

_CONFIG_CATEGORY_NAME = "KTP"
_CONFIG_CATEGORY_DESCRIPTION = "KTP North Plugin"


_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'KTP north plugin',
        'type': 'string',
        'default': 'ktp_north',
        'readonly': 'true'
    },
    'enable': {
        'description': 'Enable ktp plugin',
        'type': 'boolean',
        'default': 'false',
        'displayName': 'Enabled',
        'order': "3"
    },
    'url': {
        'description': 'Destination URL',
        'type': 'string',
        'default': 'https://measurements.com',
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
    'system_id': {
        'description': 'System id',
        'type': 'string',
        'default': 'system_id',
        'order': '1',
        'displayName': 'System_id'
    },
    'key_id': {
        'description': 'Key id',
        'type': 'string',
        'default': 'test',
        'order': '1',
        'displayName': 'Key_id'
    },
    'wma_filter': {
        'description': 'Wma_filter to select',
        'type': 'string',
        'default': 'wma_filter',
        'order': '1',
        'displayName': 'Wma_filter'
    }       
}


def plugin_info():
    """ Returns information about the plugin
    Args:
    Returns:
        dict: plugin information
    Raises:
    """
    return {
        'name': 'ktp_north',
        'version': '1.0.0',
        'type': 'north',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    handle = copy.deepcopy(config)
    return handle


async def plugin_send(handle, payload, stream_id): #is necessary otherwise unresponsive behavior #stream_id (log?) 
     
    # Select wma_filter
    wma_filter = handle['wma_filter']['value']
    
    # Initialize reading
    reading = payload[0]
    # Search for selected wma_filter
    for pld in payload:
        if wma_filter in pld['reading'].keys():
           reading = pld
    
    # Check for selected wma_filter
    if wma_filter not in reading['reading'].keys():
        is_data_sent = True
        new_position = 0
        num_sent = 1
        return is_data_sent, new_position, num_sent
    
    # Set url and credentials
    measurement_url = handle['url']['value']
        
    credentials = (handle['user_id']['value'], handle['user_pw']['value'])
    system_id = handle['system_id']['value']
    params = {'key': handle['key_id']['value']}
    #params = {'key': 'test'}
    proxies= None    
    
    # Transform reading to requested format
    # Time format
    date_time_str =reading['user_ts'] 
    date_time_obj =  datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f%z')
    date_time_obj = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S%z")
    # Data/reading format
    new_data = []   
    new_data.append({"datetime": date_time_obj,"output": reading['reading'][wma_filter] })
    # Payload format
    new_payload = {}
    new_payload["sid"] = system_id
    new_payload["data"] = new_data
    
    try:
        # Take off....
        res = requests.post(measurement_url, params=params, json=new_payload, auth=credentials, proxies=proxies)
        
        is_data_sent = True
        new_position = 0
        num_sent = 1

    except asyncio.CancelledError:      
        #pass
        is_data_sent = False
        new_position = 0
        num_sent = 0
        return is_data_sent, new_position, num_sent
    else:
        return is_data_sent, new_position, num_sent

    
def plugin_shutdown(config):
    pass


# TODO: North plugin can not be reconfigured? (per callback mechanism)
def plugin_reconfigure():
    pass
