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
import logging
from openerp import tools
from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
from urllib import urlencode
from urlparse import urljoin
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class duplicate_analysis_report(orm.Model):

    _name = "duplicate.analysis.report"
    _description = "Contact Analysis Report"
    _auto = False
    _columns = {
        'id': fields.char('ID'),
        'orig_id': fields.integer('Original ID'),
        'model': fields.char('Models'),
        'name': fields.char('Name'),
        'partner_name': fields.char('Name'),
        'seq': fields.integer('Sequence'),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'duplicate_analysis_report')
        cr.execute("""
            create or replace view duplicate_analysis_report as (
                SELECT concat('3.',pc.id) as id,
                       pc.id as orig_id,
                       partner.display_name as partner_name,
                       a.name as name,
                       cast('postal.coordinate' as varchar(20)) as model,
                       cast('3' as integer) as seq
                FROM postal_coordinate pc,address_address a,res_partner partner
                WHERE pc.address_id = a.id
                      AND
                      pc.is_duplicate_detected = TRUE
                      AND
                      pc.partner_id = partner.id

                UNION

                SELECT concat('4.',phc.id) as id,
                       phc.id as orig_id,
                       partner.display_name as partner_name,
                       ph.name as name,
                       cast('phone.coordinate' as varchar(20)) as model,
                       cast('4' as integer) as seq
                FROM phone_coordinate phc,phone_phone ph,res_partner partner
                WHERE
                    phc.phone_id = ph.id
                    AND
                    phc.is_duplicate_detected = TRUE
                    AND
                    phc.partner_id = partner.id

                UNION

                SELECT concat('2.',e.id) as id,
                       e.id as orig_id,
                       partner.display_name as partner_name,
                       e.email as name,
                       cast('email.coordinate' as varchar(20)) as model,
                       cast('2' as integer) as seq
                FROM email_coordinate e,res_partner partner
                WHERE e.is_duplicate_detected = TRUE
                      AND
                      e.partner_id = partner.id

                UNION

                SELECT concat('1.',id) as id,
                       id as orig_id,
                       to_char(birth_date,'YYYY/MM/DD') as partner_name,
                       display_name as name,
                       cast('res.partner' as varchar(20)) as model,
                       cast('1' as integer) as seq
                FROM res_partner
                WHERE is_duplicate_detected = TRUE

                ORDER BY seq,name
            )
        """)

# public methods

    def process_notify_duplicates(self, cr, uid, ids=None, force_send=False, context=None):
        """
        =========================
        process_notify_duplicates
        =========================
        :type force_send: boolean
        :param force_send: If no duplicates found force a mail to say there are
                           no duplicates
        **Note**
        This method will search duplicates and will send an email to  the users
        in charge of the configuration
        """
        uid = SUPERUSER_ID
        model, group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ficep_base', 'ficep_res_groups_configurator')
        configurator_group = self.pool.get(model).browse(cr, uid, [group_id], context=context)[0]
        if configurator_group.users:
            partner_ids = [(p.partner_id.id)for p in configurator_group.users]
            if partner_ids:
                subject = _('Ficep: Duplicates Summary')
                sort_by = 'seq ASC,name ASC'
                groups = self.read_group(cr, uid, [], self._columns.keys(), ['model'], limit=80, context=context, orderby=sort_by)
                if groups:
                    content_text = ['<table>']
                    for model in [(group['__domain']) for group in groups]:
                        ir_model = self.pool.get('ir.model')
                        model_id = ir_model.search(cr, uid, [('model', '=', model[0][2])], context=context)
                        model_name = ir_model.read(cr, uid, model_id, ['name'], context=context)[0]['name']
                        content_text.append('<tr><th><u><b>Duplicates for %s</b></u></th></tr>' % model_name)
                        result = self.search_read(cr, uid, domain=model, fields=self._columns.keys(), order=sort_by)
                        for duplicate in result:
                            partner_name = duplicate['partner_name'] if duplicate['partner_name'] else ''
                            content_text.append('<tr><td><b>%s</b</td><td> %s </td></tr>' % (partner_name, self.get_partner_access_link(cr, uid, duplicate['model'], duplicate['orig_id'], url_name=duplicate['name'], context=context)))
                    content_text.append('</table>')
                elif force_send:
                    content_text.append(_('There are no duplicates'))
                else:
                    return -1
                text_body = ''.join(content_text)
                recipient_ids = [[6, False, partner_ids]]
                return self.pool.get('mail.mail').create(cr, uid, {'subject': subject,
                                                                   'recipient_ids': recipient_ids,
                                                                   'body_html': text_body,
                                                                   }, context=context)
            return -1

    def get_partner_access_link(self, cr, uid, model, object_id, url_name='OpenERP', context=None):
        """
        =======================
        get_partner_access_link
        =======================
        :type model: string
        :param model: model technical name
        :type object_id: integer
        :param object_id: model object id
        :type url_name: string
        :param url_name: name of the url, default: OpenERP
        :rtype: string
        :rparam: an html link to read the object concerned
        """
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        # the parameters to encode for the query and fragment part of url
        query = {'db': cr.dbname}
        fragment = {
            'action': 'mail.action_mail_redirect',
        }
        fragment.update(model=model, res_id=object_id)
        url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))

        return _("""<a style='color:blue' href="%s">%s</a>""") % (url, url_name)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
