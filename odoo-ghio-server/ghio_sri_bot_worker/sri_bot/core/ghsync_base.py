#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################

from ..config import const


class GHSyncBase:
    def __init__(self, manager):
        self.manager = manager

    @property
    def uid(self):
        return self.manager.uid

    @property
    def state(self):
        return self.manager.state

    @state.setter
    def state(self, value):
        self.manager.state = value

    @property
    def action(self):
        return self.manager.action

    @action.setter
    def action(self, value):
        self.manager.action = value

    @property
    def logger(self):
        return self.manager.logger

    def info(self, message):
        return self.manager.info(message)

    def warn(self, message):
        return self.manager.warn(message)

    def error(self, message):
        return self.manager.error(message)

    def wait(self, seconds):
        return self.manager.wait(seconds)

    def run(self):
        raise NotImplementedError("Method <run> not implemented")

    def ensure_action(self, action, state=const.STATE_SUCCESS):
        return self.manager.ensure_action(action, state)
