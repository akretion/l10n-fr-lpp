# Copyright 2014-2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning
from odoo.tools import float_round, float_compare
from candybar import CandyBarCode128
from textwrap import shorten
import base64
import logging

logger = logging.getLogger(__name__)


class LppCode(models.Model):
    _name = 'lpp.code'
    _description = "LPP nomenclature of ameli.fr"
    _order = 'code'
    _rec_name = 'display_name'

    code = fields.Char('LPP Code', required=True, size=7)
    name = fields.Char('LPP Label', required=True)
    # Historize price ?
    currency_id = fields.Many2one(
        'res.currency', string='Currency', compute='_compute_currency_id', store=True)
    tax_included_price = fields.Monetary('Tax included price', currency_field='currency_id')
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
    def name_get(self):
        res = []
        for lpp in self:
            lpp_name = shorten(lpp.name, 40, placeholder='...')
            res.append((lpp.id, '[%s] %s' % (lpp.code, lpp_name)))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if name and operator == 'ilike':
            recs = self.search([('code', '=ilike', name + '%')] + args, limit=limit)
            if recs:
                return recs.name_get()
        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.constrains('code')
    def check_code(self):
        for lpp in self:
            if not lpp.code.isdigit():
                raise ValidationError(_(
                    "The LPP code '%s' should only contain digits!") % lpp.code)

    @api.depends('code')  # it seems we need to have one, otherwise it is never computed
    def _compute_currency_id(self):
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
        checksum = chr(remainder + 32)
        return checksum

    @api.depends('code')
    def _compute_code128(self):
        for lpp in self:
            code = lpp.code
            code128 = False
            if code:
                startb = chr(209)
                stop = chr(211)
                checksum = self._compute_code128_checksum(code)
                code128 = startb + code + checksum + stop
            lpp.code128 = code128

    @api.depends('code')
    def _compute_code128_barcode(self):
        for lpp in self:
            code128_barcode = False
            if lpp.code:
                candybarcode = CandyBarCode128.CandyBar128(contents=lpp.code)
                img = candybarcode.generate_barcode()
                code128_barcode = base64.b64encode(img)
            lpp.code128_barcode = code128_barcode

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
        company = self.env.company
        ccur = company.currency_id
        if not company.lpp_sale_tax_id:
            action = self.env.ref('account.action_account_config')
            msg = _(
                "Missing 'Sale Tax on Products with LPP' on company '%s'. "
                "Please go to Account Configuration.") % company.display_name
            raise RedirectWarning(
                msg, action.id, _('Go to the configuration panel'))
        lpp_sale_tax = company.lpp_sale_tax_id
        price_include = lpp_sale_tax.price_include
        prec = self.env['decimal.precision'].precision_get('Product Price')
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
                    price = ccur.round(raw_price)
                for pt in lpp.product_tmpl_ids:
                    list_price = pt.lpp_factor * price
                    if float_compare(list_price, pt.list_price, precision_digits=prec):
                        pt.write({'list_price': list_price})
                        pt.message_post(body=_("Sales price updated via the LPP product price update wizard."))
                        logger.info(
                            'Price updated to %s for product %s '
                            'with LPP %s factor %d',
                            list_price, pt.display_name, lpp.code, pt.lpp_factor)
                    else:
                        logger.info('Price of product %s with LPP %s factor %d is unchanged (%s)', pt.display_name, lpp.code, pt.lpp_factor, list_price)
