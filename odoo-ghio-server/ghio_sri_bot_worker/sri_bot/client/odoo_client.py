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
from ..core.ghsync_base import GHSyncBase


class OdooClient(GHSyncBase):
    def __init__(self, manager, url, database, username, password):
        if url.endswith('/'):
            url = url[:-1]

        super().__init__(manager)

        self._url = url
        self._database = database
        self._username = username
        self._password = password
        self._user_id = None

        if isinstance(username, int):
            self._user_id = username

        self._client = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    @property
    def user_id(self):
        if not self._user_id and isinstance(self._username, str):
            common = xmlrpc.client.ServerProxy(f'{self._url}/xmlrpc/2/common')
            try:
                self._user_id = common.authenticate(self._database, self._username, self._password, {})
            except xmlrpc.client.Fault:
                self.state = const.STATE_ERROR
        return self._user_id

    def execute(self, model, method, *args, **kwargs):
        return self._client.execute_kw(self._database, self.user_id, self._password, model, method, args, kwargs)

    def search_read(self, model, domain, fields=None, limit=None, order=None):
        kw = {}
        if fields:
            kw['fields'] = fields
        if limit:
            kw['limit'] = limit
        if order:
            kw['order'] = order

        return self.execute(model, 'search_read', domain, **kw)

    def search(self, model, domain,  limit=None, order=None):
        kw = {}
        if limit:
            kw['limit'] = limit
        if order:
            kw['order'] = order
        return self.execute(model, 'search', domain, **kw)

    def read(self, model, ids, fields=None):
        kw = {}
        if fields:
            kw['fields'] = fields
        return self.execute(model, 'read', ids, **kw)

    def write(self, model, ids, values):
        return self.execute(model, 'write', ids, values)

    def create(self, model, values):
        return self.execute(model, 'create', values)

    def unlink(self, model, ids):
        return self.execute(model, 'unlink', ids)
