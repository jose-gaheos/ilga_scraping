#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################

{
    'name': 'GAHEOS-IO SRI-BOT Worker',
    'version': '17.0.1.0',
    'depends': [
        'ghio_server',
    ],
    'external_dependencies': {
        'python': [
            'selenium',
            'webdriver_manager',
            'chromedriver_autoinstaller',
            'selenium_stealth',
            'twocaptcha',
            'pyyaml',
            'boto3',
        ],
    },
    'author': 'GAHEOS S.A.',
    'description': 'GAHEOS-IO SRI-BOT Worker',
    'category': 'Hidden/Tools',
    'website': "https://www.gaheos.com",
    'license': 'OPL-1',
    'data': [
        'security/ir.model.access.csv',
        'data/services.xml',

        'views/worker.xml',
        'views/process.xml',
        'views/files.xml',

        'views/menu.xml',
    ],
}

