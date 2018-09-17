# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo import tools


class VirtualMasterPartner(models.Model):

    _name = 'virtual.master.partner'
    _description = "Virtual Master Partner"
    _auto = False

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner')
    membership_state_id = fields.Many2one(
        comodel_name='membership.state', string='Membership State')
    display_name = fields.Char()
    technical_name = fields.Char()
    identifier = fields.Integer(string='Number', group_operator='min')
    lastname = fields.Char()
    firstname = fields.Char()
    birthdate_date = fields.Date(string='Birth Date')
    is_company = fields.Boolean()
    postal_coordinate_id = fields.Integer(
        string='Postal Coordinate ID', group_operator='min')
    email_coordinate_id = fields.Integer(
        string='Email Coordinate ID', group_operator='min')
    email = fields.Char(string='Email Coordinate')
    postal = fields.Char(string='Postal Coordinate')
    email_is_main = fields.Boolean(string='Email is Main')
    postal_is_main = fields.Boolean(string='Postal is Main')
    email_unauthorized = fields.Boolean()
    postal_unauthorized = fields.Boolean()
    email_failure_counter = fields.Integer(string='Email Bounce Counter')
    postal_failure_counter = fields.Integer(string='Postal Bounce Counter')
    zip = fields.Char("Zip Code")
    country_id = fields.Many2one(
        comodel_name='res.country', string='Country')
    int_instance_id = fields.Many2one(
        comodel_name='int.instance', string='Internal Instance')
    active = fields.Boolean()

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'virtual_master_partner')
        self.env.cr.execute("""
        create or replace view virtual_master_partner as (
        SELECT
            p.id as partner_id,
            p.membership_state_id as membership_state_id,
            p.technical_name as technical_name,
            p.select_name as display_name,
            p.identifier as identifier,
            p.lastname as lastname,
            p.firstname as firstname,
            p.birthdate_date as birthdate_date,
            p.is_company as is_company,

            e.failure_counter as email_failure_counter,
            pc.failure_counter as postal_failure_counter,

            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,

            e.is_main as email_is_main,
            pc.is_main as postal_is_main,

            adr.zip as zip,
            adr.country_id as country_id,

            e.unauthorized as email_unauthorized,
            pc.unauthorized as postal_unauthorized,

            NULL::int AS int_instance_id,

            CASE
                WHEN pc.vip is TRUE
                THEN 'VIP'
                ELSE adr.name
            END as postal,
            CASE
                WHEN e.vip is TRUE
                THEN 'VIP'
                ELSE e.email
            END as email,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM
            res_partner p

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active IS TRUE)

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active IS TRUE)

        LEFT OUTER JOIN
            address_address adr
        ON (adr.id = pc.address_id)

        WHERE p.active IS TRUE
            )""")
