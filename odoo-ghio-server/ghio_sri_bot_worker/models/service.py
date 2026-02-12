#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################
import datetime
import uuid

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.ghio_core import errors, ghio
from ..sri_bot.ghsync_sri import GHSyncSRI


class SRIAuthenticationError(errors.GHIOError):
    code = 'SRI_AUTHENTICATION_ERROR'
    message = _('SRI Authentication Error')


class Service(models.Model):
    _inherit = 'ghio.service'

    code = fields.Selection(
        selection_add=[
            ('sri_bot_worker', 'SRI-BOT Worker'),
        ],
        ondelete={
            'sri_bot_worker': 'set default',
        }
    )
    sri_bot_worker_last_run = fields.Date(
        string='SRI-BOT Server Last Run',
        readonly=True,
    )

    @property
    def _config_headless(self):
        return not bool(self.env['ir.config_parameter'].sudo().get_param('ghio.sri_bot_worker_no_headless', False))

    @property
    def _config_home_path(self):
        return self.env['ir.config_parameter'].sudo().get_param('ghio.sri_bot_worker_home_path', '/tmp/sri_dw')

    def _get_parent_required_codes(self):
        return super()._get_parent_required_codes() + ['sri_bot_worker']

    def _get_ghio_server_install_codes(self):
        return super()._get_ghio_server_install_codes() + ['sri_bot_worker']

    def _get_parent_supported_codes(self):
        if self.code == 'sri_bot_worker':
            return ['ghio_server']
        return super()._get_parent_supported_codes()

    def _get_identity_required_codes(self):
        return super()._get_identity_required_codes() + ['sri_bot_worker']

    def _ghio_server_service_install_sri_bot_worker(self, data):
        self_sudo = self.sudo()

        if not data:
            raise ValidationError(_('Data is required'))

        if not data.get('service_id'):
            raise ValidationError(_('Service ID is required'))

        service = self_sudo.create({
            'name': _('SRI-BOT Worker: %s', self_sudo.ghio_server_customer_id.name),
            'code': 'sri_bot_worker',
            'parent_id': self_sudo.id
        })

        return service._sri_bot_worker_register(
            data.get('service_id'),
            data.get('ruc'),
            data.get('additional_ci'),
            data.get('password'),
            data.get('identity_token'),
        )

    @ghio.method('sri_bot_worker.register', token_type='access')
    def _sri_bot_worker_register(
            self,
            service_id,
            ruc,
            additional_ci,
            password,
            identity_token
    ):
        self_sudo = self.sudo()

        if not identity_token:
            raise ValidationError(_('Identity Token is required'))

        tokens = self_sudo._send(
            'ghio.get_tokens',
            {},
            url=f'{self_sudo.ghio_server_db_url}/ghio',
            service_id=service_id,
            token=identity_token
        )

        if not tokens:
            raise ValidationError(_('Invalid Identity Token'))

        return self_sudo._ghio_sri_worker_update_credentials(
            ruc,
            additional_ci,
            password,
            service_id,
            tokens['access_token'],
            tokens['refresh_token']
        )

    @ghio.method('sri_bot_worker.update_settings', token_type='access')
    def _ghio_sri_bot_worker_update_settings(self, document_types=None):
        worker = self.env['ghio.sri_bot.worker'].sudo().search([('service_id', '=', self.id)], limit=1)

        if not worker:
            raise ValidationError(_('SRI-BOT Credentials not found'))

        worker._update_settings(document_types=document_types)

        return True

    @ghio.method('sri_bot_worker.update_credentials', token_type='access')
    def _ghio_sri_worker_update_credentials(self, ruc, additional_ci, password, service_id, access_token=None,
                                            refresh_token=None):

        self_sudo = self.sudo()
        self_sudo._ghio_sri_worker_check_credentials(ruc, additional_ci, password)

        worker = self_sudo.env['ghio.sri_bot.worker'].search([('service_id', '=', self.id)], limit=1)

        worker_data = {
            'ruc': ruc,
            'additional_ci': additional_ci,
            'password': password,
            'state': 'enabled',
            'db_service_id': service_id,
            'service_id': self_sudo.id,
        }

        if not worker:
            if access_token and refresh_token:
                worker_data['access_token'] = access_token
                worker_data['refresh_token'] = refresh_token
            else:
                raise ValidationError(_('Access Token and Refresh Token are required'))

            self_sudo.env['ghio.sri_bot.worker'].create(worker_data)
        else:
            worker.write(worker_data)

        self_sudo.write({
            'state': 'enabled',
            'server_handshake': True,
            'server_handshake_date': fields.Datetime.now(),
        })

        return self_sudo.id

    def _ghio_sri_worker_check_credentials(self, ruc, additional_ci, password):
        if not ruc:
            raise ValidationError(_('RUC is required'))

        if len(ruc) != 13:
            raise ValidationError(_('RUC must be 13 digits'))

        if additional_ci and len(additional_ci) != 10:
            raise ValidationError(_('Additional CI must be 10 digits'))

        if not password:
            raise ValidationError(_('Password is required'))

        sri = self.env['ghio.sri_bot.worker'].sudo()._get_sri_client_standalone(
            str(self.id),
            ruc,
            additional_ci,
            password
        )

        if not sri.test_auth():
            raise SRIAuthenticationError

        return True

    @api.model
    def _ghio_sri_bot_worker_create_tasks(self, date=None):
        date = date or fields.Date.context_today(self)

        workers = self.env['ghio.sri_bot.worker.process'].sudo()

        for cred in self.env['ghio.sri_bot.worker'].sudo().search(
                [
                    ('state', '=', 'enabled'),
                    ('service_id.server_handshake', '=', True),
                    ('service_id.code', '=', 'sri_bot_worker'),
                    ('service_id.state', '=', 'enabled'),
                ]
        ):
            workers |= workers.create({
                'date': date,
                'service_id': cred.service_id.id,
                'worker_id': cred.id,
            })

        workers._action_open()
        return True
