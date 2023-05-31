# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Instance moves
    log_instance_join = fields.Boolean(
        "Log when partner joins an instance",
        config_parameter="changes_report.log_instance_join",
    )
    instance_join_seq = fields.Integer(
        "Instance join sequence",
        config_parameter="changes_report.instance_join_seq",
        default=100,
    )
    log_instance_leave = fields.Boolean(
        "Log when partner leaves an instance",
        config_parameter="changes_report.log_instance_leave",
    )
    instance_leave_seq = fields.Integer(
        "Instance leave sequence",
        config_parameter="changes_report.instance_leave_seq",
        default=520,
    )

    # State changes
    log_supporter = fields.Boolean(
        "Log when partner becomes a supporter",
        config_parameter="changes_report.log_supporter",
    )
    supporter_seq = fields.Integer(
        "New supporter sequence",
        config_parameter="changes_report.supporter_seq",
        default=120,
    )
    log_member_committee = fields.Boolean(
        "Log when partner becomes a member committee",
        config_parameter="changes_report.log_member_committee",
    )
    member_committee_seq = fields.Integer(
        "New member committee sequence",
        config_parameter="changes_report.member_committee_seq",
        default=160,
    )
    log_renewal = fields.Boolean(
        "Log when partner renews his subscription",
        config_parameter="changes_report.log_renewal",
    )
    renewal_seq = fields.Integer(
        "Renewal sequence", config_parameter="changes_report.renewal_seq", default=200
    )
    log_member = fields.Boolean(
        "Log when partner becomes a member",
        config_parameter="changes_report.log_member",
    )
    member_seq = fields.Integer(
        "New member sequence", config_parameter="changes_report.member_seq", default=210
    )
    log_former_member_committee = fields.Boolean(
        "Log when partner becomes a former member committee",
        config_parameter="changes_report.log_former_member_committee",
    )
    former_member_committee_seq = fields.Integer(
        "New former member committee sequence",
        config_parameter="changes_report.former_member_committee_seq",
        default=230,
    )
    log_former_member = fields.Boolean(
        "Log when partner becomes a former member",
        config_parameter="changes_report.log_former_member",
    )
    former_member_seq = fields.Integer(
        "New former member sequence",
        config_parameter="changes_report.former_member_seq",
        default=300,
    )
    log_former_supporter = fields.Boolean(
        "Log when partner becomes a former supporter",
        config_parameter="changes_report.log_former_supporter",
    )
    former_supporter_seq = fields.Integer(
        "New former supporter sequence",
        config_parameter="changes_report.former_supporter_seq",
        default=310,
    )
    log_break_former_member = fields.Boolean(
        "Log when partner becomes a break former member",
        config_parameter="changes_report.log_break_former_member",
    )
    break_former_member_seq = fields.Integer(
        "New break former member sequence",
        config_parameter="changes_report.break_former_member_seq",
        default=400,
    )
    log_expulsion_former_member = fields.Boolean(
        "Log when partner becomes an expulsion former member",
        config_parameter="changes_report.log_expulsion_former_member",
    )
    expulsion_former_member_seq = fields.Integer(
        "New expulsion former member sequence",
        config_parameter="changes_report.expulsion_former_member_seq",
        default=410,
    )
    log_inappropriate_former_member = fields.Boolean(
        "Log when partner becomes an inappropriate former member",
        config_parameter="changes_report.log_inappropriate_former_member",
    )
    inappropriate_former_member_seq = fields.Integer(
        "New inappropriate former member sequence",
        config_parameter="changes_report.inappropriate_former_member_seq",
        default=420,
    )
    log_resignation_former_member = fields.Boolean(
        "Log when partner becomes a resignation former member",
        config_parameter="changes_report.log_resignation_former_member",
    )
    resignation_former_member_seq = fields.Integer(
        "New resignation former member sequence",
        config_parameter="changes_report.resignation_former_member_seq",
        default=430,
    )

    # Partner updates
    log_voluntaries_changes = fields.Boolean(
        "Log voluntaries changes",
        config_parameter="changes_report.log_voluntaries_changes",
    )
    voluntaries_changes_seq = fields.Integer(
        "Voluntaries changes sequence",
        default=220,
        config_parameter="changes_report.voluntaries_changes_seq",
    )
    log_email_changes = fields.Boolean(
        "Log email changes", config_parameter="changes_report.log_email_changes"
    )
    email_changes_seq = fields.Integer(
        "Email changes sequence",
        default=500,
        config_parameter="changes_report.email_changes_seq",
    )
    log_address_changes = fields.Boolean(
        "Log address changes", config_parameter="changes_report.log_address_changes"
    )
    address_changes_seq = fields.Integer(
        "Address changes sequence",
        default=510,
        config_parameter="changes_report.address_changes_seq",
    )
    log_global_opt_out_changes = fields.Boolean(
        "Log global opt-out changes",
        config_parameter="changes_report.log_global_opt_out_changes",
    )
    global_opt_out_changes_seq = fields.Integer(
        "Global opt-out changes sequence",
        default=515,
        config_parameter="changes_report.global_opt_out_changes_seq",
    )
