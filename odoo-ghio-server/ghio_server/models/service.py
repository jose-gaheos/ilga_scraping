#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.ghio_core import errors, ghio


class Service(models.Model):
    _inherit = 'ghio.service'

    def _valid_field_parameter(self, field, name):
        return name == 'required_if_provider' or super()._valid_field_parameter(field, name)

    code = fields.Selection(
        selection_add=[
            ('ghio_server', 'GAHEOS-IO Server'),
        ],
        ondelete={
            'ghio_server': 'cascade',
        }
    )

    ghio_server_db_name = fields.Char(
        string='Database Name',
        compute='_compute_ghio_server_db_name',
        store=True,
        readonly=False,
        recursive=True,
        copy=False,
    )
    ghio_server_db_uuid = fields.Char(
        string='Database UUID',
        compute='_compute_ghio_server_db_uuid',
        store=True,
        readonly=False,
        recursive=True,
        copy=False,
    )
    ghio_server_db_url = fields.Char(
        string='Database URL',
        compute='_compute_ghio_server_db_url',
        store=True,
        readonly=False,
        recursive=True,
        copy=False,
    )
    ghio_server_customer_id = fields.Many2one(
        string='Service Customer',
        comodel_name='res.partner',
        compute='_compute_ghio_server_customer',
        store=True,
        readonly=False,
        recursive=True,
        ondelete='restrict',
        required_if_provider='ghio_server'
    )
    ghio_server_customer_invoice_id = fields.Many2one(
        string='Service Final Customer',
        comodel_name='res.partner',
        compute='_compute_ghio_server_customer_invoice',
        store=True,
        readonly=False,
        recursive=True,
        ondelete='restrict',
        required_if_provider='ghio_server',
    )

    @ghio.method('ghio_server.handshake', token_type='access')
    def _ghio_server_handshake(self, db_name, db_uuid, db_url):
        self.sudo().write({
            'ghio_server_db_name': db_name,
            'ghio_server_db_uuid': db_uuid,
            'ghio_server_db_url': db_url,
            'server_handshake': True,
            'server_handshake_date': fields.Datetime.now(),
        })
        return True

    @ghio.method('ghio_server.service_install', token_type='access')
    def _ghio_server_service_install(self, service, data):
        if service not in self._get_ghio_server_install_codes():
            raise errors.ServiceNotInstallableError(_('Service "%s" cannot be installed', service))
        method_name = f'_ghio_server_service_install_{service}'
        if not hasattr(self, method_name):
            raise errors.MethodNotFoundError()
        return getattr(self, method_name)(data)

    def ghio_server_show_token(self):
        return self._check_ghio_server_identity().button_show_token_identity()

    def ghio_server_generate_token(self):
        return self._check_ghio_server_identity(reset=True).button_show_token_identity()

    @api.model
    def _get_ghio_server_install_codes(self):
        return []

    def _get_children_supported_codes(self):
        return super()._get_children_supported_codes() + ['ghio_server']

    @api.depends('parent_id.ghio_server_db_name')
    def _compute_ghio_server_db_name(self):
        for record in self:
            record.ghio_server_db_name = record.parent_id.ghio_server_db_name

    @api.depends('parent_id.ghio_server_db_uuid')
    def _compute_ghio_server_db_uuid(self):
        for record in self:
            record.ghio_server_db_uuid = record.parent_id.ghio_server_db_uuid

    @api.depends('parent_id.ghio_server_db_url')
    def _compute_ghio_server_db_url(self):
        for record in self:
            record.ghio_server_db_url = record.parent_id.ghio_server_db_url

    @api.depends('parent_id.ghio_server_customer_id')
    def _compute_ghio_server_customer(self):
        for record in self:
            record.ghio_server_customer_id = record.parent_id.ghio_server_customer_id

    @api.depends('parent_id.ghio_server_customer_invoice_id')
    def _compute_ghio_server_customer_invoice(self):
        for record in self:
            record.ghio_server_customer_invoice_id = record.parent_id.ghio_server_customer_invoice_id

    @api.onchange('ghio_server_customer_id')
    def _onchange_ghio_server_customer(self):
        self.ghio_server_customer_invoice_id = self.ghio_server_customer_id.commercial_partner_id

    def _action_enable_ghio_server(self):
        identity = self._check_ghio_server_identity()
        self.state = 'enabled'
        return identity.button_show_token_identity()

    def _check_ghio_server_identity(self, reset=False):
        if self.identity_id.mode != 'service':
            self.identity_id.unlink()
        if not self.ghio_server_customer_id:
            raise UserError(_('Service Customer is required'))
        if not self.ghio_server_customer_id.email:
            raise UserError(_('Service Customer must have an email address'))

        user = self.env['res.users'].sudo().with_context(active_test=False, no_reset_password=True).search(
            [('partner_id', '=', self.ghio_server_customer_id.id)])

        if not user:
            if user.search([('login', '=', self.ghio_server_customer_id.email)]):
                raise UserError(_('A user with the same login already exists'))
            user = user.create({
                'name': self.ghio_server_customer_id.name,
                'login': self.ghio_server_customer_id.email,
                'email': self.ghio_server_customer_id.email,
                'partner_id': self.ghio_server_customer_id.id,
                'company_id': self.env.company.id,
                'company_ids': [(4, self.env.company.id)],
                'active': True,
                'groups_id': [(6, 0, self.env.ref('base.group_portal').ids)],
            })

        if not user.active:
            raise UserError(_('Portal User is not active'))

        if not self.identity_id:
            self.identity_id = self.env['ghio.identity'].create({
                'name': self.name,
                'mode': 'service',
                'user_id': user.id,
            })

        if self.identity_id.token_state_identity != 'enabled' or reset:
            self.identity_id.sudo()._generate_token('identity')
            self.identity_id.sudo()._revoke_token('access')
            self.identity_id.sudo()._revoke_token('refresh')

        if self.identity_id.token_state_identity != 'enabled':
            raise UserError(_('An error occurred while creating/updating the identity'))

        return self.identity_id
