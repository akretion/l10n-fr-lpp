# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from candybar import CandyBarCode128


class LppCode(models.Model):
    _name = 'lpp.code'
    _description = "LPP nomenclature of ameli.fr"
    _order = 'code'
    _rec_name = 'display_name'

    code = fields.Char('LPP Code', required=True, size=7)
    name = fields.Char('LPP Label', required=True)
    tax_included_price = fields.Monetary('Tax included price')
    # Historize price ?
    currency_id = fields.Many2one(
        'res.currency', string='Currency', compute='compute_currency_id',
        readonly=True, store=True)
    display_name = fields.Char(
        compute='compute_display_name_field',
        readonly=True, store=True)
    product_tmpl_ids = fields.One2many(
        'product.template', 'lpp_code_id', string='Products', readonly=True)
    active = fields.Boolean(default=True)
    code128 = fields.Char(
        compute='_compute_code128', string="Code 128 String",
        readonly=True, store=True,
        help="Code 128 string representation (with checksum) of LPP Code.")
    code128_barcode = fields.Binary(
        compute='_compute_code128_barcode', readonly=True,
        string='Code128 Barcode')

    @api.multi
    @api.depends('code', 'name')
    def compute_display_name_field(self):
        for lpp in self:
            lpp.display_name = u'[%s] %s' % (lpp.code, lpp.name)

    @api.multi
    @api.constrains('code')
    def check_code(self):
        for lpp in self:
            if not lpp.code.isdigit():
                raise ValidationError(_(
                    "The LPP code '%s' should only contain digits!")
                    % lpp.code)

    @api.multi
    def compute_currency_id(self):
        eur_id = self.env.ref('base.EUR').id
        for lpp in self:
            lpp.currency_id = eur_id

    def _compute_code128_checksum(self, code):
        # This will only work in our scenario
        # This is NOT a full implementation of code128 checksum
        csum = 104  # Start B
        i = 0
        for char in code:
            i += 1
            assert code.isdigit()
            char_val = ord(char) - 32
            csum += char_val * i
        remainder = csum % 103
        checksum = unichr(remainder + 32)
        return checksum

    @api.multi
    @api.depends('code')
    def _compute_code128(self):
        for lpp in self:
            code = lpp.code
            startb = unichr(209)
            stop = unichr(211)
            checksum = self._compute_code128_checksum(code)
            lpp.code128 = startb + code + checksum + stop

    @api.multi
    @api.depends('code')
    def _compute_code128_barcode(self):
        for lpp in self:
            candybarcode = CandyBarCode128.CandyBar128(contents=lpp.code)
            img = candybarcode.generate_barcode()
            lpp.code128_barcode = img.encode('base64')

    _sql_constraints = [(
        'unique_code',
        'unique(code)',
        'This LPP code already exists',
        )]
