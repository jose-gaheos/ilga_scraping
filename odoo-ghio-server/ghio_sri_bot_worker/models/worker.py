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
import uuid

import boto3
from logging import getLogger
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from ..sri_bot.ghsync_sri import GHSyncSRI

_logger = getLogger(__name__)


class SRIBOTWorkerCredentials(models.Model):
    _name = 'ghio.sri_bot.worker'
    _description = 'SRI-BOT Worker Client'
    _rec_names_search = ['ruc', 'db_service_id']

    db_service_id = fields.Integer(
        string='DB Service ID',
        required=True,
    )
    document_type_01 = fields.Boolean(
        string='Download Invoices',
        default=False,
    )
    document_type_04 = fields.Boolean(
        string='Download Credit Notes',
        default=False,
    )
    document_type_05 = fields.Boolean(
        string='Download Debit Notes',
        default=False,
    )
    document_type_07 = fields.Boolean(
        string='Download Withholding Receipts',
        default=False,
    )
    state = fields.Selection(
        string='State',
        selection=[
            ('pending', 'Pending'),
            ('enabled', 'Enabled'),
            ('disabled', 'Disabled'),
            ('error', 'Error'),
        ],
        default='pending',
        required=True,
    )
    ruc = fields.Char(
        string='RUC',
        required=True,
    )
    additional_ci = fields.Char(
        string='Additional CI',
    )
    password = fields.Char(
        string='Password',
    )
    password_saved = fields.Boolean(
        string='Password Saved',
        default=False,
    )
    access_token = fields.Char(
        string='Access Token',
    )
    refresh_token = fields.Char(
        string='Refresh Token',
    )
    service_id = fields.Many2one(
        string='Service',
        comodel_name='ghio.service',
        index=True,
        required=True,
        ondelete='cascade',
    )

    @property
    def _config_home_path(self):
        return self.env['ir.config_parameter'].sudo().get_param('ghio.sri_bot_worker_home_path',
                                                                '/mnt/odoo-shared/sri_bot')

    @property
    def _config_selenium_url(self):
        return self.env['ir.config_parameter'].sudo().get_param('ghio.sri_bot_worker_selenium_url',
                                                                'http://localhost:4444/wd/hub')

    @property
    def _config_solver_token(self):
        return self.env['ir.config_parameter'].sudo().get_param('ghio.sri_bot_worker_solver_apikey', None)

    def _update_settings(self, document_types=None):
        data = {}

        if document_types is not None and isinstance(document_types, list):
            data['document_type_01'] = 'invoice' in document_types
            data['document_type_04'] = 'credit_note' in document_types
            data['document_type_05'] = 'debit_note' in document_types
            data['document_type_07'] = 'withholding' in document_types

        if data:
            self.write(data)

        return True

    @api.depends('ruc', 'db_service_id', 'service_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'{rec.ruc} :: {rec.service_id.ghio_server_db_url}/ghio/{rec.db_service_id} ({rec.service_id.id})'

    def _get_sri_client(self):
        self.ensure_one()
        return self._get_sri_client_standalone(
            self.service_id.id,
            self.ruc,
            self.additional_ci,
            self.password,
        )

    def _get_sri_client_standalone(self, service_id, ruc, additional_ci, password):
        return GHSyncSRI(
            uid=f'{ruc}-{service_id}',
            username=ruc,
            password=password,
            extra_ci=additional_ci or None,

            selenium_url=self._config_selenium_url,
            home_path=self._config_home_path,
            solver_apikey=self._config_solver_token,
            logs_tracking='error',
        )


class SRIBOTWorker(models.Model):
    _name = 'ghio.sri_bot.worker.process'
    _description = 'GAHEOS-IO SRI-BOT Worker'
    _order = 'create_date DESC, id DESC'

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('download', 'Downloaded'),
            ('upload', 'Uploaded'),
            ('done', 'Sent'),
            ('error', 'Error'),
            ('empty', 'Empty'),
        ],
        string='State',
        required=True,
        default='draft'
    )
    state_auth = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('authenticated', 'Authenticated'),
            ('error', 'Error'),
        ],
        string='Authentication State',
        required=True,
        default='pending'
    )
    force_month = fields.Boolean(
        string='Force Month',
        default=False,
    )
    document_type_01 = fields.Boolean(
        string='Download Invoices',
        compute='_compute_document_type',
        store=True,
        readonly=False,
    )
    document_type_04 = fields.Boolean(
        string='Download Credit Notes',
        compute='_compute_document_type',
        store=True,
        readonly=False,
    )
    document_type_05 = fields.Boolean(
        string='Download Debit Notes',
        compute='_compute_document_type',
        store=True,
        readonly=False,
    )
    document_type_07 = fields.Boolean(
        string='Download Withholding Receipts',
        compute='_compute_document_type',
        store=True,
        readonly=False,
    )
    final_count = fields.Integer(
        string='Uploaded Files',
        readonly=True,
    )
    service_id = fields.Many2one(
        comodel_name='ghio.service',
        string='Service',
        required=True,
        ondelete='cascade',
    )
    worker_id = fields.Many2one(
        comodel_name='ghio.sri_bot.worker',
        string='Worker',
        required=True
    )
    has_error = fields.Boolean(
        string='Has Error',
        default=False
    )
    file_count = fields.Integer(
        string='Files Count',
        compute='_compute_file_count'
    )
    stage_ids = fields.One2many(
        comodel_name='ghio.sri_bot.worker.stage',
        inverse_name='process_id',
        string='Stages',
        copy=False,
    )

    @api.depends('worker_id')
    def _compute_document_type(self):
        for rec in self:
            rec.document_type_01 = rec.worker_id.document_type_01
            rec.document_type_04 = rec.worker_id.document_type_04
            rec.document_type_05 = rec.worker_id.document_type_05
            rec.document_type_07 = rec.worker_id.document_type_07

    def open_files(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('ghio_sri_bot_worker.action_ghio_sri_bot_worker_file')
        action['context'] = {'default_process_id': self.id, 'search_default_process_id': self.id}
        action['domain'] = [('process_id', '=', self.id)]
        return action

    @api.model
    def _filter_access_keys(self, access_keys):
        self.ensure_one()
        if not access_keys:
            return
        access_keys_dict = dict(access_keys)
        self.env.cr.execute(
            "SELECT name FROM ghio_sri_bot_worker_file WHERE name IN %s",
            (tuple(access_keys_dict.keys()),)
        )
        for access_key, in self.env.cr.fetchall():
            access_key_index = access_keys_dict.pop(access_key, None)
            if access_key_index is not None:
                yield access_key, access_key_index, True
        for access_key, access_key_index in access_keys_dict.items():
            yield access_key, access_key_index, False

    def _action_open(self):
        self._generate_stages()
        for rec in self:
            if not rec.stage_ids:
                rec.state = 'empty'
            else:
                rec.state = 'open'

    def button_open(self):
        self.ensure_one()
        self._action_open()
        return True

    def button_authenticate(self):
        self.ensure_one()
        sri = self.worker_id._get_sri_client()
        res = sri.test_auth()
        return res

    def button_download(self):
        self.ensure_one()
        sri = self.worker_id._get_sri_client()

        sri.download(self)

        self.has_error = bool(self.stage_ids.filtered(lambda x: x.state == 'error'))

        if not self.stage_ids.filtered(lambda x: x.state == 'pending'):
            self._compute_file_count()

            if self.file_count:
                self.state = 'download'
            elif self.has_error:
                self.state = 'error'
            else:
                self.state = 'empty'

        self.env.cr.commit()

        return True

    def button_send(self):
        file_rows = []

        for file in self.env['ghio.sri_bot.worker.file'].search(
                [('process_id', '=', self.id), ('state', '=', 'uploaded')]):
            file_rows.append([file.name, file.document_type, file.path_xml, file.path_pdf])

        self.service_id._send(
            'sri_bot.sync_sri_files',
            {
                'name': f'SRI-BOT/{self.date.strftime("%Y")}/{self.date.strftime("%m")}/{str(self.id).zfill(5)}',
                'date': self.date.strftime('%Y-%m-%d'),
                'rows': file_rows,
            },
            url=f'{self.service_id.ghio_server_db_url}/ghio',
            service_id=self.worker_id.db_service_id,
            token=self.worker_id.access_token
        )

        self.write({
            'state': 'done',
            'final_count': len(file_rows),
        })

        return True

    def button_upload_s3(self):
        self.ensure_one()

        uploader = S3WorkerFileUploader(self)

        files_to_remove = []

        for file in self.env['ghio.sri_bot.worker.file'].search(
                [('process_id', '=', self.id), ('state', '=', 'pending')]):
            files_to_remove += uploader.upload(file)

        for file_path in files_to_remove:
            try:
                os.remove(file_path)
            except Exception as e:
                pass

        self.state = 'upload'

        return True

    def _generate_stages(self):
        stages_to_create = []

        for rec in self:
            if rec.state != 'draft':
                continue
            if rec.force_month:
                date_ranges = [
                    [
                        rec.date.replace(day=1),
                        rec.date.replace(day=1) + relativedelta(months=1, days=-1)
                    ]
                ]
            else:
                date_ranges = generate_date_ranges(rec.date)

            for date_from, date_to in date_ranges:
                stage_template = {
                    'date_from': date_from,
                    'date_to': date_to,
                    'process_id': rec.id,
                }
                if rec.document_type_01:
                    stage_template['document_type'] = '1'
                    stages_to_create.append(stage_template.copy())
                if rec.document_type_07:
                    stage_template['document_type'] = '6'
                    stages_to_create.append(stage_template.copy())
                if rec.document_type_04:
                    stage_template['document_type'] = '4'
                    stages_to_create.append(stage_template.copy())
                if rec.document_type_05:
                    stage_template['document_type'] = '5'
                    stages_to_create.append(stage_template.copy())

        self.env['ghio.sri_bot.worker.stage'].create(stages_to_create)

    def _compute_file_count(self):
        result = dict(
            (data['process_id'][0], data['process_id_count'])
            for data in self.env['ghio.sri_bot.worker.file'].sudo().read_group(
                domain=[('process_id', 'in', self.ids)],
                fields=['process_id'],
                groupby=['process_id'])
        )
        for rec in self:
            rec.file_count = result.get(rec.id, 0)

    @api.depends('worker_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.worker_id.display_name


class SRIBOTWorkerStage(models.Model):
    _name = 'ghio.sri_bot.worker.stage'
    _description = 'GAHEOS-IO SRI-BOT Stage'
    _order = 'date_from DESC, id ASC'

    date_from = fields.Date(
        string='Date From',
        required=True
    )
    date_to = fields.Date(
        string='Date To',
        required=True
    )
    state = fields.Selection(
        string='State',
        selection=[
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('error', 'Error'),
        ],
        required=True,
        default='pending'
    )
    document_type = fields.Selection(
        string='Document Type',
        selection=[
            ('1', 'Factura'),
            ('6', 'Comprobante de Retención'),
            ('3', 'Nota de Crédito'),
            ('4', 'Nota de Débito'),
        ],
        required=True
    )
    year = fields.Char(
        string='Year',
        compute='_compute_date',
        store=True
    )
    month = fields.Char(
        string='Month',
        compute='_compute_date',
        store=True
    )
    day = fields.Char(
        string='Day',
        compute='_compute_date',
        store=True
    )
    process_id = fields.Many2one(
        comodel_name='ghio.sri_bot.worker.process',
        string='Worker',
        required=True,
        ondelete='cascade',
    )

    @api.depends('date_from', 'date_to')
    def _compute_date(self):
        for record in self:
            record.year = str(record.date_from.year)
            record.month = str(record.date_from.month)
            record.day = str(record.date_from.day) if record.date_from == record.date_to else '0'


class SRIBOTWorkerFile(models.Model):
    _name = 'ghio.sri_bot.worker.file'
    _description = 'SRI-BOT Worker File'
    _order = 'id DESC'

    name = fields.Char(
        string='Access Key',
        required=True
    )
    state = fields.Selection(
        string='State',
        selection=[
            ('pending', 'Pending'),
            ('uploaded', 'Uploaded'),
            ('existing', 'Existing'),
            ('error', 'Error'),
        ],
        required=True,
        default='pending'
    )
    date = fields.Date(
        string='Date',
        compute='_compute_access_key',
        store=True
    )
    document_type = fields.Selection(
        string='Document Type',
        selection=[
            ('01', 'Factura'),
            ('04', 'Nota de Crédito'),
            ('05', 'Nota de Débito'),
            ('06', 'Guía de Remisión'),
            ('07', 'Comprobante de Retención'),
            ('08', 'Liquidación de Compra'),
            ('09', 'Comprobante de Venta'),
        ],
        compute='_compute_access_key',
        store=True
    )
    ruc = fields.Char(
        string='RUC',
        compute='_compute_access_key',
        store=True
    )
    environment = fields.Selection(
        string='Environment',
        selection=[
            ('1', 'Pruebas'),
            ('2', 'Producción'),
        ],
        compute='_compute_access_key',
        store=True
    )
    document_number = fields.Char(
        string='Document Number',
        compute='_compute_access_key',
        store=True
    )
    path_xml = fields.Char(
        string='XML File Path',
    )
    path_pdf = fields.Char(
        string='PDF File Path',
    )
    process_id = fields.Many2one(
        comodel_name='ghio.sri_bot.worker.process',
        string='Worker',
        required=True,
        ondelete='cascade',
    )

    @api.depends('name')
    def _compute_access_key(self):
        for record in self:
            date = record.name[0:8]
            record.document_type = record.name[8:10]
            record.date = f'{date[4:]}-{date[2:4]}-{date[0:2]}'
            record.ruc = record.name[10:23]
            record.environment = record.name[23:24]
            record.document_number = '%s-%s-%s' % (record.name[24:27], record.name[27:30], record.name[30:39])


class S3WorkerFileUploader:
    def __init__(self, worker):
        self.worker = worker
        self.env = worker.env
        self.bucket = None
        self.region = None
        self.url = None
        self.s3 = None
        self._init_s3()

    def _init_s3(self):
        s3_credentials = self.env['ir.config_parameter'].sudo().get_param('ghio.sri_bot_worker_s3_credentials', None)

        if not s3_credentials:
            raise UserError(_('AWS S3 credentials are not configured'))

        bucket, region, access_key, secret_key = s3_credentials.split(':')
        self.bucket = bucket
        self.region = region
        self.url = f'https://{bucket}.s3.{region}.amazonaws.com'
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

    def upload(self, file):
        create_path = '/'.join([
            f'{file.process_id.worker_id.ruc}-{file.process_id.worker_id.service_id.id}',
            str(file.date.year),
            str(file.date.month).zfill(2),
            file.document_type,
            file.ruc,
            file.document_number
        ])
        file_data = {}
        files_to_remove = []
        for ext, path in [('xml', file.path_xml), ('pdf', file.path_pdf)]:
            if path and os.path.exists(path):
                filename = f'{create_path}.{ext}'
                try:
                    self.s3.upload_file(path, self.bucket, filename)
                    file_data[f'path_{ext}'] = f'{self.url}/{filename}'
                    files_to_remove.append(path)
                    _logger.info(f'File {file.name}.{ext} uploaded to s3://{self.bucket}/{filename}')
                except Exception as e:
                    _logger.error(
                        f'Error uploading file {file.name}.{ext} to s3://{self.bucket}/{filename}: {e}')
                    file_data[f'path_{ext}'] = ''
                    return []
        if file_data:
            file_data['state'] = 'uploaded'
            file.write(file_data)
        return files_to_remove


def generate_date_ranges(input_date):
    input_date = input_date - relativedelta(days=1)
    date_ranges = []

    if input_date.weekday() == 5:
        start_of_week = max(input_date - relativedelta(days=6), input_date.replace(day=1))
        date_ranges.append([
            start_of_week,
            input_date
        ])
    else:
        date_ranges.append([input_date, input_date])

    if input_date.day == 10:
        last_day_prev_month = (input_date - relativedelta(months=1)).replace(day=1) + relativedelta(months=1, days=-1)
        first_day_prev_month = last_day_prev_month - relativedelta(days=10)
        date_ranges.append([
            first_day_prev_month,
            last_day_prev_month
        ])
    return date_ranges
