# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.mozaik_mandate.int_mandate import int_mandate
from openerp.addons.mozaik_mandate.ext_mandate import ext_mandate
from openerp.addons.mozaik_base import url


class mandates_analysis_report(orm.Model):
    _name = "mandates.analysis.report"
    _description = 'Mandates Analysis Report'
    _auto = False

    _mandate_models = ['int.mandate', 'ext.mandate']

    _columns = {
        'model': fields.char('Models'),
        'id': fields.char('ID'),
        'designation_int_assembly_id': fields.integer('Designation Assembly'),
        'months_before_end_of_mandate': fields.integer('Alert Delay (#Months)'
                                                       ),
        'remaining_months_before_end_of_mandate': fields.integer(
                                    'Remaining Months before End of Mandate')
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'mandates_analysis_report')
        cr.execute("""
            create or replace view mandates_analysis_report as (
                SELECT *
                  FROM (
                    SELECT 'int.mandate' AS model,
                           mandate.id,
                           mandate.designation_int_assembly_id,
                           CASE WHEN mandate.months_before_end_of_mandate > 0
                                THEN mandate.months_before_end_of_mandate
                                WHEN assembly.months_before_end_of_mandate > 0
                                THEN assembly.months_before_end_of_mandate
                                ELSE category.months_before_end_of_mandate
                           END AS months_before_end_of_mandate,
                           ROUND(
                          (EXTRACT(year FROM age(deadline_date,now()))*12)
                        +  EXTRACT(month FROM age(deadline_date,now()))
                        + (EXTRACT(day FROM age(deadline_date,now()))/30)
                           ) AS remaining_months_before_end_of_mandate
                    FROM  int_mandate           AS mandate
                     JOIN int_assembly          AS assembly
                       ON assembly.id = mandate.int_assembly_id
                     JOIN int_assembly_category AS category
                      ON category.id = assembly.assembly_category_id
                    WHERE end_date IS Null
                      AND alert_date IS NULL
                      AND deadline_date > now()

                    UNION

                    SELECT 'ext.mandate' AS model,
                           mandate.id,
                           mandate.designation_int_assembly_id,
                           CASE WHEN mandate.months_before_end_of_mandate > 0
                                THEN mandate.months_before_end_of_mandate
                                WHEN assembly.months_before_end_of_mandate > 0
                                THEN assembly.months_before_end_of_mandate
                                ELSE category.months_before_end_of_mandate
                           END AS months_before_end_of_mandate,
                           ROUND(
                          (EXTRACT(year FROM age(deadline_date,now()))*12)
                        +  EXTRACT(month FROM age(deadline_date,now()))
                        + (EXTRACT(day FROM age(deadline_date,now()))/30)
                           ) AS remaining_months_before_end_of_mandate
                    FROM  ext_mandate           AS mandate
                     JOIN ext_assembly          AS assembly
                       ON assembly.id = mandate.ext_assembly_id
                     JOIN ext_assembly_category AS category
                       ON category.id = assembly.assembly_category_id
                    WHERE end_date IS Null
                      AND alert_date IS NULL
                      AND deadline_date > now()
                       ) AS mandates
                   WHERE remaining_months_before_end_of_mandate
                         <=
                         months_before_end_of_mandate
                   AND months_before_end_of_mandate > 0
                   ORDER BY 1,3
            )
        """)
# public methods

    def process_notify_ending_mandates(self, cr, uid, ids=None, context=None):
        """
        ==============================
        process_notify_ending_mandates
        ==============================
        Search ending mandates and send an alert to secretariat
        """
        if not context:
            context = self.pool.get('res.users').context_get(cr, uid,
                                                             context=context)
        assembly_pool = self.pool.get('int.assembly')
        alert_dict = {}
        for mandate_model in self._mandate_models:
            mandates = self.search_read(cr, uid,
                                        domain=[('model', '=', mandate_model)],
                                        context=context)
            for mandate in mandates:
                secretariat_id = assembly_pool.get_secretariat_assembly_id(
              cr, uid, mandate['designation_int_assembly_id'], context=context)
                if secretariat_id:
                    mandate = self.pool.get(mandate['model']).browse(cr, uid,
                                                mandate['id'], context=context)
                    if secretariat_id in alert_dict:
                        alert_dict[secretariat_id].extend([mandate])
                    else:
                        alert_dict[secretariat_id] = [mandate]

        for secretary_id in alert_dict:
            secretary = assembly_pool.browse(cr, uid, secretary_id,
                                             context=context)
            mandate_list = alert_dict[secretary_id]
            content_text = ['<p><table>']
            content_text.append(
                            '<tr><th colspan="2"><br/><u>%s</u></th></tr>' %
                            _('Ending mandates alerts report'))
            for mandate in mandate_list:
                assembly_name = ''
                if isinstance(mandate._model, int_mandate):
                    assembly_name = mandate.int_assembly_id.name
                elif isinstance(mandate._model, ext_mandate):
                    assembly_name = mandate.ext_assembly_id.name

                content_text.append('<tr><td><b>%s</b</td><td>%s</td><td>%s\
                                     </td><td><a style="color:blue" \
                                     href="%s">(%s)</a></td></tr>' % \
                               (mandate.partner_id.name,
                                mandate.mandate_category_id.name,
                                assembly_name,
                                url.get_document_url(self, cr, uid,
                                                     mandate._model._name,
                                                     mandate.id,
                                                     context=context),
                                self.pool.get('res.lang').format_date(cr, uid,
                                      mandate.deadline_date, context=context)))
                mandate._model.write(cr, uid, mandate.id,
                                     {'alert_date': fields.date.today()},
                                     context=context)
            content_text.append('</table></p>')

            mail_vals = {
                'subject': _('Mozaik: Ending Mandates Summary - %s') %
                self.pool.get('res.lang').format_date(cr,
                                                    uid,
                                                    fields.date.today(cr, uid),
                                                    context=context),
                'body_html': '\n'.join(content_text),
                'recipient_ids': [[6, False, [secretary.partner_id.id]]],
            }
            self.pool.get('mail.mail').create(cr, uid, mail_vals,
                                              context=context)
        return True
