# -*- coding: utf-8 -*-

from openerp import models, fields, tools


class MassMailingReport(models.Model):
    _inherit = 'mail.statistics.report'

    group_id = fields.Many2one(
        'mail.mass_mailing.group', string='Group', readonly=True)
    trial = fields.Char(readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'mail_statistics_report')
        cr.execute("""
            CREATE OR REPLACE VIEW mail_statistics_report AS (
                SELECT
                    min(ms.id) as id,
                    ms.scheduled::date as scheduled_date,
                    mm.name as name,
                    mc.name as campaign,
                    count(ms.bounced) as bounced,
                    count(ms.sent) as sent,
                    (count(ms.sent) - count(ms.bounced)) as delivered,
                    count(ms.opened) as opened,
                    count(ms.replied) as replied,
                    mm.state,
                    mm.email_from,
                    mm.group_id,
                    mm.name||' (#'||(ROW_NUMBER() OVER (PARTITION BY mm.group_id ORDER BY mm.id))||')' AS trial
                FROM
                    mail_mail_statistics as ms
                    left join mail_mass_mailing as mm ON (ms.mass_mailing_id=mm.id)
                    left join mail_mass_mailing_campaign as mc ON (ms.mass_mailing_campaign_id=mc.id)
                GROUP BY ms.scheduled::date, mm.name, mc.name, mm.state, mm.email_from, mm.group_id, mm.id
            )""")
