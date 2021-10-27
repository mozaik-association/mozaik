# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import fields, models, tools


class MassMailingReport(models.Model):
    _inherit = "mailing.trace.report"

    group_id = fields.Many2one(
        comodel_name="mail.mass_mailing.group",
        string="Group",
        readonly=True,
    )
    trial = fields.Char(
        readonly=True,
    )

    def init(self):
        cr = self.env.cr
        view_name = self._table
        tools.drop_view_if_exists(cr, view_name)
        query_values = {
            "table_name": AsIs(view_name),
        }
        query = """
CREATE OR REPLACE VIEW %(table_name)s AS (
SELECT
    min(ms.id) as id,
    ms.scheduled as scheduled_date,
    utm_source.name as name,
    utm_campaign.name as campaign,
    count(ms.bounced) as bounced,
    count(ms.sent) as sent,
    (count(ms.sent) - count(ms.bounced)) as delivered,
    count(ms.opened) as opened,
    count(ms.replied) as replied,
    mm.state,
    mm.email_from,
    mm.group_id,
    utm_source.name||' (#'||(ROW_NUMBER() OVER (
        PARTITION BY mm.group_id
        ORDER BY mm.id
    ))||')' AS trial
FROM
    mailing_trace as ms
    left join mailing_mailing as mm ON (ms.mass_mailing_id=mm.id)
    left join utm_campaign as utm_campaign ON (
        mm.campaign_id = utm_campaign.id)
    left join utm_source as utm_source ON (mm.source_id = utm_source.id)
GROUP BY
    ms.scheduled, utm_source.name, utm_campaign.name, mm.state, mm.email_from,
    mm.group_id, mm.id
)
        """
        cr.execute(query, query_values)
