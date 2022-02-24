# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class VirtualMasterPartner(models.Model):

    _name = "virtual.master.partner"
    _description = "Virtual Master Partner"
    _auto = False

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    membership_state_id = fields.Many2one(
        comodel_name="membership.state", string="Membership State"
    )
    display_name = fields.Char()
    technical_name = fields.Char()
    identifier = fields.Char(string="Number", group_operator="min")
    lastname = fields.Char()
    firstname = fields.Char()
    birthdate_date = fields.Date(string="Birth Date")
    is_company = fields.Boolean()
    email = fields.Char(string="Email Coordinate")
    # email_failure_counter = fields.Integer(string='Email Bounce Counter')
    # postal_failure_counter = fields.Integer(string='Postal Bounce Counter')
    zip = fields.Char("Zip Code")
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    int_instance_id = fields.Many2one(
        comodel_name="int.instance", string="Internal Instance"
    )
    active = fields.Boolean()
    type = fields.Char()

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "virtual_master_partner")
        self.env.cr.execute(
            """
        create or replace view virtual_master_partner as (
        SELECT
            p.id as id,
            p.id as partner_id,
            p.membership_state_id as membership_state_id,
            p.technical_name as technical_name,
            p.select_name as display_name,
            p.identifier as identifier,
            p.lastname as lastname,
            p.firstname as firstname,
            p.birthdate_date as birthdate_date,
            p.is_company as is_company,
            p.type as type,

            adr.zip as zip,
            adr.country_id as country_id,

            NULL::int AS int_instance_id,

            p.email as email,
            CASE
                WHEN (p.email IS NOT NULL OR adr.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM
            res_partner p


        LEFT OUTER JOIN
            address_address adr
        ON (adr.id = p.address_address_id)

        WHERE p.active IS TRUE
            )"""
        )
