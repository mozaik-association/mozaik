Mozaik
======

A suite of Odoo modules to manage large associative organizations (members, committees, subscriptions, ...).

A sandbox environnement is available [here](http://mozaik.odoodemo.acsone.eu/web). A demo user with guest/guest credentials can be used to log on.

Summary
-------

[Ecolo](http://www.ecolo.be) (the green Belgian political party) entrusted to [Acsone](http://www.acsone.eu) the development of Mozaik, an application to manage and communicate with it's human resources: be it members (and manage membership), supporters, Ecolo politicians and political representatives in the boards of various organisations, and state owned agencies.

By choice model of society, Ecolo since it's beginning always used as many FOSS as possible for itself, and also promoted a maximum use of OOS by the states administrations, that's why you can get the whole application and modules of Mozaik open sourced under AGPL.

What can you do with Mozaik ?
-----------------------------

- the follow-up of the members, supporters, politicians and representatives with a complete membership workflow and a fluent and performing communication
- the follow-up of the electoral process from the setting up of the lists of candidates to the electoral results
- the follow-up of the mandates including their renewal and the detection of suspicious holding multiple offices
- the follow-up of the membership fees and retrocessions
- the definition of the state's structure and party's organisation

Mozaik required the development of some extensions to the basis features:
- advanced CRM: multi-email, multi-address, local address validation, multi-phone, multi-relationship between partners, management of duplicates, ...
- dynamic distribution lists (complex expressions associated with static opt-in/opt-out lists based on a multi-model search engine) together with mass (mailing) features
- online help (editable by power users), currently in French
- SSO-type authentication method.

Who can benefit from Mozaik ?
-----------------------------

- nearly *as is* for the Belgians political parties, but also for any political party in the world, as they probably have to manage members, membership fees, supporters, politicians, electoral process, and state and organisation structures.
- for medium to big ngo, that have also to manage members, and sometimes complex organisational structures that can evolve
- for state administrations, that could implement our state structure modules
- for any kind of organisations, that could benefit from advanced CRM features and/or mass functions

More technically
----------------

The application is intended for Odoo v8, but is currently mostly coded using the classic OpenERP api.

Some more generic modules have been move to other repositories:
- [Acsone Addons](https://github.com/acsone/acsone-addons) for distribution lists and newsletters (```distribution_list```)
- [OCA/web](https://github.com/OCA/web) for online help (```help_online```)
- [OCA/Server Tools](https://github.com/OCA/server-tools) for SSO authentication (```auth_from_http_remote_user```)

A special module is provided to quickly build a non empty sandbox database: ```mozaik_sample_accounting```.

List of dependencies needed to the whole project can be consulted in the ```mozaik_base/__openerp__.py``` manifest.

