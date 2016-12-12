# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
    display_name = fields.Char(compute='compute_display_name_field')
    product_tmpl_ids = fields.One2many(
        'product.template', 'lpp_code_id', string='Products', readonly=True)
    active = fields.Boolean(default=True)

    @api.multi
    @api.depends('code', 'name')
    def compute_display_name_field(self):
        for lpp in self:
            lpp.display_name = u'%s %s' % (lpp.code, lpp.name)

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

    _sql_constraints = [(
        'unique_code',
        'unique(code)',
        'This LPP code already exists',
        )]
