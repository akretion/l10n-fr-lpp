# -*- coding: utf-8 -*-
# Copyright 2014-2019 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from tempfile import TemporaryFile
import unicodecsv
import logging

logger = logging.getLogger(__name__)


class LppCsvImport(models.TransientModel):
    _name = 'lpp.csv.import'
    _description = 'LPP: CSV Import'

    csv_file = fields.Binary(string='CSV File', required=True)
    filename = fields.Char(string='Filename')
    update_product = fields.Boolean(
        string='Also Update Product Prices', default=True)

    def run(self):
        self.ensure_one()
        fileobj = TemporaryFile('w+')
        fileobj.write(self.csv_file.decode('base64'))
        fileobj.seek(0)
        reader = unicodecsv.reader(
            fileobj,
            delimiter=';',
            quoting=unicodecsv.QUOTE_MINIMAL,
            encoding='latin1')
        i = 0
        lppcode2obj = {}
        lpps = self.env['lpp.code'].search(
            ['|', ('active', '=', True), ('active', '=', False)])
        for lpp in lpps:
            lppcode2obj[lpp.code] = lpp
        update_product = self.update_product
        for row in reader:
            i += 1
            logger.debug('row %d=%s', i, row)
            if len(row) < 2:
                continue
            if not row[0] or not row[1]:
                continue
            for j in [0, 1]:
                if row[j]:
                    row[j] = row[j].strip()
                else:
                    row[j] = False
            if not row[0].isdigit():
                logger.warning('Skipping line %d with LPP code %s', i, row[0])
                continue
            if row[0] not in lppcode2obj:
                logger.warning('LPP code %s is not in Odoo', row[0])
                continue
            lpp = lppcode2obj[row[0]]
            price = False
            try:
                price = float(row[1].replace(',', '.'))
            except Exception:
                logger.warning(
                    'Could not parse price %s of LPP %s', row[1], row[0])
                continue
            if price < 0.01:
                logger.warning(
                    'Wrong price %s on LPP %s', row[1], row[0])
                continue
            old_price = lpp.tax_included_price
            lpp.tax_included_price = price
            logger.info(
                'LPP %s (ID %d) updated from price %s to price %s',
                row[0], lpp.id, old_price, price)
            if update_product:
                lpp.update_product_price()

        fileobj.close()
        return
