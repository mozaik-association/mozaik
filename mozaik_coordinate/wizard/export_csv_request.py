COMMON_REQUEST = """
SELECT
 p.identifier,
 p.name,
 p.lastname,
 p.firstname,
 p.usual_lastname,
 p.usual_firstname,
 p.reference,
 p.birth_date,
 p.gender,
 p.tongue,
 p.website,
 p.secondary_website,
 CASE
  WHEN cc IS NOT NULL
  THEN cc.line
  ELSE p.printable_name
 END AS printable_name,
 cc.id as co_residency_id,
 cc.line2 as co_residency,
 instance.name as instance,
 ms.name as status,
 ipl.name as power_name,
 pc.is_main as adr_main,
 pc.unauthorized as adr_unauthorized,
 pc.vip as adr_vip,
 CASE
  WHEN pc.vip = True
  THEN 'VIP'
  ELSE address.street2
 END AS street2,
 CASE
  WHEN pc.vip = True
  THEN 'VIP'
  ELSE address.street
 END AS street,
 CASE
  WHEN pc.vip = True
  THEN 'VIP'
  ELSE address.zip
 END AS zip,
 CASE
  WHEN pc.vip = True
  THEN 'VIP'
  ELSE address.city
 END AS city,
 CASE
  WHEN pc.vip = True
  THEN 'VIP'
  ELSE country.name
 END AS country_name,
 CASE
  WHEN pc.vip = True
  THEN 'VIP'
  ELSE country.code
 END AS country_code,
 fix.is_main as fix_main,
 fix.unauthorized as fix_unauthorized,
 fix.vip as fix_vip,
 CASE
  WHEN fix.vip = True
  THEN 'VIP'
  ELSE fix_phone.name
 END AS fix,
 mobile.is_main as mobile_main,
 mobile.unauthorized as mobile_unauthorized,
 mobile.vip as mobile_vip,
 CASE
  WHEN mobile.vip = True
  THEN 'VIP'
  ELSE mobile_phone.name
 END AS mobile,
 fax.is_main as fax_main,
 fax.unauthorized as fax_unauthorized,
 fax.vip as fax_vip,
 CASE
  WHEN mobile.vip = True
  THEN 'VIP'
  ELSE fax_phone.name
 END AS fax,
 ec.is_main as email_main,
 ec.unauthorized as email_unauthorized,
 ec.vip as email_vip,
 ec.email
"""
VIRTUAL_TARGET_REQUEST = """
%s
FROM
virtual_target vt

JOIN res_partner p
 ON p.id = vt.partner_id

LEFT OUTER JOIN int_instance instance
 ON instance.id = p.int_instance_id

LEFT OUTER JOIN membership_state ms
 ON ms.id = p.membership_state_id

LEFT OUTER JOIN int_power_level ipl
 ON instance.power_level_id = ipl.id

LEFT OUTER JOIN postal_coordinate pc
 ON pc.id = vt.postal_coordinate_id AND
 pc.active = True

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
 ON fix_phone.id = fix.id

LEFT OUTER JOIN phone_coordinate mobile
 ON mobile.partner_id = p.id AND
 mobile.is_main = True AND
 mobile.coordinate_type = 'mobile' AND
 mobile.active = True

LEFT OUTER JOIN phone_phone mobile_phone
 ON mobile_phone.id = mobile.id

LEFT OUTER JOIN phone_coordinate fax
 ON fax.partner_id = p.id AND
 fax.is_main = True AND
 fax.coordinate_type = 'fix' AND
 fax.active = True

LEFT OUTER JOIN phone_phone fax_phone
 ON fax_phone.id = fax.id

LEFT OUTER JOIN email_coordinate ec
 ON ec.id = vt.email_coordinate_id AND
 ec.active = True

""" % COMMON_REQUEST

EMAIL_COORDINATE_REQUEST = """
%s
FROM email_coordinate ec

JOIN res_partner p
 ON p.id = ec.partner_id

LEFT OUTER JOIN int_instance instance
 ON instance.id = p.int_instance_id

LEFT OUTER JOIN membership_state ms
 ON ms.id = p.membership_state_id

LEFT OUTER JOIN int_power_level ipl
 ON instance.power_level_id = ipl.id

LEFT OUTER JOIN postal_coordinate pc
 ON pc.partner_id = p.id AND
 pc.is_main = True AND
 pc.active = True

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
 ON fix_phone.id = fix.id

LEFT OUTER JOIN phone_coordinate mobile
 ON mobile.partner_id = p.id AND
 mobile.is_main = True AND
 mobile.coordinate_type = 'mobile' AND
 mobile.active = True

LEFT OUTER JOIN phone_phone mobile_phone
 ON mobile_phone.id = mobile.id

LEFT OUTER JOIN phone_coordinate fax
 ON fax.partner_id = p.id AND
 fax.is_main = True AND
 fax.coordinate_type = 'fix' AND
 fax.active = True

LEFT OUTER JOIN phone_phone fax_phone
 ON fax_phone.id = fax.id
""" % COMMON_REQUEST

POSTAL_COORDINATE_REQUEST = """
%s

FROM postal_coordinate pc

JOIN res_partner p
 ON p.id = pc.partner_id

LEFT OUTER JOIN int_instance instance
 ON instance.id = p.int_instance_id

LEFT OUTER JOIN membership_state ms
 ON ms.id = p.membership_state_id

LEFT OUTER JOIN int_power_level ipl
 ON instance.power_level_id = ipl.id

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
 ON fix_phone.id = fix.id

LEFT OUTER JOIN phone_coordinate mobile
 ON mobile.partner_id = p.id AND
 mobile.is_main = True AND
 mobile.coordinate_type = 'mobile' AND
 mobile.active = True

LEFT OUTER JOIN phone_phone mobile_phone
 ON mobile_phone.id = mobile.id

LEFT OUTER JOIN phone_coordinate fax
 ON fax.partner_id = p.id AND
 fax.is_main = True AND
 fax.coordinate_type = 'fix' AND
 fax.active = True

LEFT OUTER JOIN phone_phone fax_phone
 ON fax_phone.id = fax.id

LEFT OUTER JOIN email_coordinate ec
 ON ec.partner_id = p.id AND
 ec.is_main = True AND
 ec.active = True

""" % COMMON_REQUEST
