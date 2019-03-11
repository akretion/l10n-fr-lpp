# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning
from odoo.tools import float_round
from candybar import CandyBarCode128
import logging

logger = logging.getLogger(__name__)


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

    @api.depends('code', 'name')
    def compute_display_name_field(self):
        for lpp in self:
            lpp.display_name = u'[%s] %s' % (lpp.code, lpp.name)

    @api.constrains('code')
    def check_code(self):
        for lpp in self:
            if not lpp.code.isdigit():
                raise ValidationError(_(
                    "The LPP code '%s' should only contain digits!")
                    % lpp.code)

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

    @api.depends('code')
    def _compute_code128(self):
        for lpp in self:
            code = lpp.code
            startb = unichr(209)
            stop = unichr(211)
            checksum = self._compute_code128_checksum(code)
            lpp.code128 = startb + code + checksum + stop

    @api.depends('code')
    def _compute_code128_barcode(self):
        for lpp in self:
            candybarcode = CandyBarCode128.CandyBar128(contents=lpp.code)
            img = candybarcode.generate_barcode()
            lpp.code128_barcode = img.encode('base64')

    _sql_constraints = [
        (
            'unique_code',
            'unique(code)',
            'This LPP code already exists',
        ),
        (
            'tax_included_price_positive',
            'CHECK (tax_included_price >= 0)',
            "The value of the field 'Tax included price' must be positive or 0"
        )]

    def update_product_price(self):
        company = self.env.user.company_id
        if not company.lpp_sale_tax_id:
            action = self.env.ref('account.action_account_config')
            msg = _(
                "Missing 'Sale Tax on Products with LPP' on company '%s'. "
                "Please go to Account Configuration.") % company.name
            raise RedirectWarning(
                msg, action.id, _('Go to the configuration panel'))
        lpp_sale_tax = company.lpp_sale_tax_id
        price_include = lpp_sale_tax.price_include
        assert lpp_sale_tax.amount_type == 'percent'
        for lpp in self:
            if lpp.tax_included_price < 0.01:
                msg = _(
                    "Cannot update price for LPP %s because its price (%s) "
                    "is < 0.01") % (lpp.code, lpp.tax_included_price)
                if self._context.get('mass_update'):
                    logger.warning(msg)
                    continue
                else:
                    raise UserError(msg)
            if lpp.product_tmpl_ids:
                for pt in lpp.product_tmpl_ids:
                    if not pt.taxes_id:
                        raise UserError(_(
                            "Missing Sale Tax on product '%s'.")
                            % pt.display_name)
                    if pt.taxes_id[0] != lpp_sale_tax:
                        raise UserError(_(
                            "On product '%s', the Sale Tax is '%s'. It should "
                            "have the LPP Sale Tax of the company i.e. '%s'.")
                            % (pt.display_name, pt.taxes_id[0].name,
                               lpp_sale_tax.name))

                if price_include:
                    price = lpp.tax_included_price
                else:
                    # There are no methods in Odoo to compute HT from TTC using
                    # a tax-exclude tax
                    raw_price = lpp.tax_included_price * 100.0 / \
                        (100.0 + lpp_sale_tax.amount)
                    price = float_round(
                        raw_price,
                        precision_rounding=company.currency_id.rounding)
                lpp.product_tmpl_ids.write(
                    {'list_price': price})
                logger.info(
                    'Price updated to %s for %d products with LPP %s',
                    price, len(lpp.product_tmpl_ids), lpp.code)
        return True
