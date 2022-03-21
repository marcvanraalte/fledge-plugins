# -*- coding: utf-8 -*-

# Fledge_BEGIN
# See: http://fledge-iot.readthedocs.io/
# Fledge_END

""" Module for WMA filter plugin

Generate Windowed Moving Average
"""

import time
import copy
import logging

from fledge.common import logger
import filter_ingest

__author__ = "Marc van Raalte"
__copyright__ = "Copyright (c) 2022 Alliander System Operations"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__, level = logging.WARN)

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Windowed Moving Average filter plugin',
        'type': 'string',
        'default': 'wma_filter',
        'readonly': 'true'
    },
    'enable': {
        'description': 'Enable wma plugin',
        'type': 'boolean',
        'default': 'false',
        'displayName': 'Enabled',
        'order': "3"
    },
    'filter_time': {
        'description': 'Interval time of the wma in seconds',
        'type': 'integer',
        'default': '10',
        'displayName': 'Filter time in seconds',
        'order': "2"
    },
    'datapoint': {
        'description': 'Datapoint name for calculated wma value',
        'type': 'string',
        'default': 'wma_filter',
        'displayName': 'WMA datapoint',
        'order': "1"
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
        'name': 'wma_filter',
        'version': '1.0.0',
        'mode': "none",
        'type': 'filter',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config, ingest_ref, callback):
    """ Initialise the plugin
    Args:
        config: JSON configuration document for the Filter plugin configuration category
        ingest_ref:
        callback:
    Returns:
        data: JSON object to be used in future calls to the plugin
    Raises:
    """
    handle = copy.deepcopy(config)

    handle['callback'] = (callback,ingest_ref)
    handle['shutdown_in_progress'] = False
    handle['datapoint'] = handle['datapoint']['value']  

    _LOGGER.debug("plugin_init for filter WMA called")
    
    reset_wma(handle)
    
    return handle

def reset_wma(handle):
    handle['xmean'] = 0
    handle['window'] = [0]*int(handle['filter_time']['value'])
    handle['counter'] = 0

def compute_wma(handle, reading):
    """ Compute WMA

    Args:
        A reading data
    """
    
    wsize = len(handle['window'])
    xmean = handle['xmean']
    window = handle['window']
    
    elem = list(reading.values())[0]  
    rot = handle['counter'] % wsize
    xlast = window[rot]
    window[rot] = elem
    xmean = (wsize*xmean + elem - xlast)/wsize
    handle['counter'] += 1
    handle['xmean'] = reading[handle['datapoint']] = xmean
    handle['window'] = window


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    """
    
    _LOGGER.debug("Old config for wma plugin {} \n new config {}".format(handle, new_config))
    new_handle = copy.deepcopy(new_config)
     
    _LOGGER.debug("plugin_init for filter WMA called")
    
    new_handle['datapoint'] = new_handle['datapoint']['value']
    reset_wma(new_handle)
    
    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        plugin shutdown
    """
    handle['shutdown_in_progress'] = True
    time.sleep(1)
   
    _LOGGER.info('filter ema plugin shutdown.')


def plugin_ingest(handle, data):
    """ Modify readings data and pass it onward

    Args:
        handle: handle returned by the plugin initialisation call
        data: readings data
    """
    
    if handle['shutdown_in_progress']:
        return

    if handle['enable']['value'] == 'false':
        # Filter not enabled, just pass data onwards
        filter_ingest.filter_ingest_callback(*handle['callback'], data)
        return

    
    for elem in data:
        compute_wma(handle, elem['readings']) 
        if handle['counter'] % (len(handle['window'])// 2) == 0:
           filter_ingest.filter_ingest_callback(*handle['callback'], [elem])
           
      
    _LOGGER.debug("wma filter_ingest done")
