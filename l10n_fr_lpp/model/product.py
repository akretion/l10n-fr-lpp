# -*- coding: utf-8 -*-
# Copyright 2014-2019 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lpp_code_id = fields.Many2one(
        'lpp.code', 'LPP Code', ondelete='restrict')
    lpp_factor = fields.Integer(string='LPP Factor', default=1)

    _sql_constraints = [(
        'lpp_factor_positive',
        'CHECK(lpp_factor > 0)',
        "The value of the field 'LPP Factor' must be positive.")]
