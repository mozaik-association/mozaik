# -*- coding: utf-8 -*-
# © 2016  Jonathan Nemry, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ExportCSVQueries(models.AbstractModel):
    _name = 'export.csv.queries'
    _auto = False

    @api.model
    def _common_request(self):
        return """
SELECT
 p.identifier,
 p.name,
 p.lastname,
 p.firstname,
 p.usual_lastname,
 p.usual_firstname,
 p.int_instance_id,
 p.reference,
 p.birth_date,
 p.gender,
 p.tongue,
 p.website,
 p.secondary_website,
 p.technical_name,
 p.local_voluntary,
 p.regional_voluntary,
 p.national_voluntary,
 p.local_only,
 CASE
  WHEN cc.line IS NOT NULL
  THEN cc.line
  ELSE p.printable_name
 END AS printable_name,
 cc.id as co_residency_id,
 cc.line2 as co_residency,
 instance.name as instance,
 p.membership_state_id as state_id,
 ipl.name as power_name,
 pc.is_main as adr_main,
 pc.unauthorized as adr_unauthorized,
 pc.vip as adr_vip,
 address.street2 as street2,
 address.street as street,
 address.zip as final_zip,
 address.city as city,
 country.id as country_id,
 country.name as country_name,
 country.code as country_code,
 fix.is_main as fix_main,
 fix.unauthorized as fix_unauthorized,
 fix.vip as fix_vip,
 fix_phone.name as fix,
 mobile.is_main as mobile_main,
 mobile.unauthorized as mobile_unauthorized,
 mobile.vip as mobile_vip,
 mobile_phone.name as mobile,
 fax.is_main as fax_main,
 fax.unauthorized as fax_unauthorized,
 fax.vip as fax_vip,
 fax_phone.name as fax,
 ec.is_main as email_main,
 ec.unauthorized as email_unauthorized,
 ec.vip as email_vip,
 ec.email
"""

    @api.model
    def _common_joins(self):
        return """
LEFT OUTER JOIN int_instance instance
 ON instance.id = p.int_instance_id

LEFT OUTER JOIN int_power_level ipl
 ON ipl.id = instance.power_level_id

LEFT OUTER JOIN address_address address
 ON address.id = pc.address_id

LEFT OUTER JOIN res_country country
 ON country.id = address.country_id

LEFT OUTER JOIN co_residency cc
 ON cc.id = pc.co_residency_id

LEFT OUTER JOIN phone_coordinate fix
 ON fix.partner_id = p.id AND
 fix.is_main = True AND
 fix.coordinate_type= 'fix' AND
 fix.active = True

LEFT OUTER JOIN phone_phone fix_phone
 ON fix_phone.id = fix.phone_id

LEFT OUTER JOIN phone_coordinate mobile
 ON mobile.partner_id = p.id AND
 mobile.is_main = True AND
 mobile.coordinate_type = 'mobile' AND
 mobile.active = True

LEFT OUTER JOIN phone_phone mobile_phone
 ON mobile_phone.id = mobile.phone_id

LEFT OUTER JOIN phone_coordinate fax
 ON fax.partner_id = p.id AND
 fax.is_main = True AND
 fax.coordinate_type = 'fax' AND
 fax.active = True

LEFT OUTER JOIN phone_phone fax_phone
 ON fax_phone.id = fax.phone_id
"""

    @api.model
    def virtual_target_request(self):
        return """
%s
FROM virtual_target vt

JOIN res_partner p
 ON p.id = vt.partner_id

LEFT OUTER JOIN email_coordinate ec
 ON ec.id = vt.email_coordinate_id AND
 ec.active = True

LEFT OUTER JOIN postal_coordinate pc
 ON pc.id = vt.postal_coordinate_id AND
 pc.active = True

%s
""" % (self._common_request(), self._common_joins())

    @api.model
    def email_coordinate_request(self):
        return """
%s
FROM email_coordinate ec

JOIN res_partner p
 ON p.id = ec.partner_id

LEFT OUTER JOIN postal_coordinate pc
 ON pc.partner_id = p.id AND
 pc.is_main = True AND
 pc.active = True

%s
""" % (self._common_request(), self._common_joins())

    @api.model
    def postal_coordinate_request(self):
        return """
%s
FROM postal_coordinate pc

JOIN res_partner p
 ON p.id = pc.partner_id

LEFT OUTER JOIN email_coordinate ec
 ON ec.partner_id = p.id AND
 ec.is_main = True AND
 ec.active = True

%s
""" % (self._common_request(), self._common_joins())
