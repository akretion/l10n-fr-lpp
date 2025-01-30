import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-akretion-l10n-fr-lpp",
    description="Meta package for akretion-l10n-fr-lpp Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-l10n_fr_lpp',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
