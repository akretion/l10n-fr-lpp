# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    lpp_code_id = fields.Many2one(
        'lpp.code', string='LPP Code', readonly=True)

    def _select(self):
        select_str = super(AccountInvoiceReport, self)._select()
        select_str += ', sub.lpp_code_id'
        return select_str

    def _sub_select(self):
        select_str = super(AccountInvoiceReport, self)._sub_select()
        select_str += ', pt.lpp_code_id'
        return select_str

    def _group_by(self):
        group_by_str = super(AccountInvoiceReport, self)._group_by()
        group_by_str += ', pt.lpp_code_id'
        return group_by_str
