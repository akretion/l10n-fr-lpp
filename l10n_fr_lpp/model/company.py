# -*- coding: utf-8 -*-
# Copyright 2014-2019 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    lpp_sale_tax_id = fields.Many2one(
        'account.tax', 'Sale Tax on Products with LPP', ondelete='restrict',
        domain=[('type_tax_use', '=', 'sale')])
