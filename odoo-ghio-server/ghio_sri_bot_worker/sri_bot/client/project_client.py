#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################
import xmlrpc

from ..config import const
from ..client.odoo_client import OdooClient
from ..core.ghsync_base import GHSyncBase


class ProjectClient(OdooClient):
    def __init__(self, manager, url, database, username, password):
        super().__init__(manager, url, database, username, password)

    def run(self):
        print(self.search('res.partner', [], limit=1))
