# Copyright 2016-2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sécurité sociale: LPP',
    'summary': 'Liste des produits et prestations (LPP) '
               'de la sécurité sociale',
    'version': '14.0.1.0.1',
    'category': 'French Localization',
    'author': "Akretion",
    'website': 'https://github.com/akretion/l10n-fr-lpp',
    'license': 'AGPL-3',
    'depends': ['sale'],
    # only needed for menu entry ; should only depend on 'product'
    'external_dependencies': {'python': ['candybar', 'unicodecsv']},
    'data': [
        'security/ir.model.access.csv',
        'views/lpp_code.xml',
        'views/product.xml',
        'views/account_invoice_report.xml',
        'views/res_config_settings_view.xml',
        'wizards/lpp_update_product_price_view.xml',
        'wizards/lpp_csv_import_view.xml',
        'data/lpp.code.csv',
    ],
    'installable': True,
}
