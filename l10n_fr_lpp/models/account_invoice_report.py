# Copyright 2019-2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    lpp_code_id = fields.Many2one(
        'lpp.code', string='LPP Code', readonly=True)

    def _select(self):
        select_str = super()._select()
        select_str += ', template.lpp_code_id'
        return select_str
