import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-mozaik",
    description="Meta package for mozaik Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-mozaik_all',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)

