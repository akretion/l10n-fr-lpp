# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class LppUpdateProductPrice(models.TransientModel):
    _name = 'lpp.update.product.price'
    _description = 'LPP: Update Products Prices'

    @api.multi
    def run(self):
        self.ensure_one()
        assert self.env.context.get('active_model') == 'lpp.code',\
            'Source model must be LPP'
        assert self.env.context.get('active_ids'), 'No LPP selected'
        lpps = self.env['lpp.code'].browse(
            self.env.context.get('active_ids'))
        lpps.with_context(mass_update=True).update_product_price()
        return
