#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################

import os
import yaml


def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def load_global_config():
    global_config_path = os.getenv('SHSYNC_SRI_CONFIG', None)
    if not global_config_path:
        raise Exception('Global config path not found')
    return load_config(global_config_path)


def load_local_config(config_path):
    return load_config(config_path)
