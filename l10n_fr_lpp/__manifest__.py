# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': u'Sécurité sociale: LPP',
    'summary': u'Liste des produits et prestations (LPP) '
               u'de la sécurité sociale',
    'version': '10.0.1.0.0',
    'category': 'French Localization',
    'author': "Akretion",
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'depends': ['sale'],
    # only needed for menu entry ; should only depend on 'product'
    'external_dependencies': {'python': ['candybar', 'unicodecsv']},
    'data': [
        'security/ir.model.access.csv',
        'views/lpp_code.xml',
        'views/product.xml',
        'views/account_config_settings_view.xml',
        'wizard/lpp_update_product_price_view.xml',
        'wizard/lpp_csv_import_view.xml',
        'data/lpp.code.csv',
    ],
    'installable': True,
}
