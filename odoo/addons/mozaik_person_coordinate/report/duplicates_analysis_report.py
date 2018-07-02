# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import tools
from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.exceptions import Warning

from openerp.addons.mozaik_base import url

_logger = logging.getLogger(__name__)
complete_group = 'mozaik_base.mozaik_res_groups_configurator'


class duplicate_analysis_report(orm.Model):
    _name = "duplicate.analysis.report"
    _description = "Duplicates Analysis Report"
    _auto = False

    _columns = {
        'id': fields.char('ID'),
        'orig_id': fields.integer('Original ID'),
        'partner_name': fields.char('Partner Name'),
        'name': fields.char('Name'),
        'model': fields.char('Models'),
        'sequence': fields.integer('Sequence'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'duplicate_analysis_report')
        cr.execute("""
            create or replace view duplicate_analysis_report as (
                SELECT concat('1.',id) as id,
                       id as orig_id,
                       display_name as partner_name,
                       to_char(birth_date,'DD/MM/YYYY') as name,
                       'res.partner'::varchar as model,
                       1 as sequence
                FROM  res_partner
                WHERE is_duplicate_detected = TRUE
                AND   active = TRUE

            UNION

                SELECT concat('2.',e.id) as id,
                       e.id as orig_id,
                       partner.display_name as partner_name,
                       e.email as name,
                       'email.coordinate'::varchar as model,
                       2 as sequence
                FROM  email_coordinate e, res_partner partner
                WHERE partner.id = e.partner_id
                AND   e.is_duplicate_detected = TRUE
                AND   e.active = TRUE

            UNION

                SELECT concat('3.',pc.id) as id,
                       pc.id as orig_id,
                       partner.display_name as partner_name,
                       a.name as name,
                       'postal.coordinate'::varchar as model,
                       3 as sequence
                FROM
                    postal_coordinate pc,
                    res_partner partner,
                    address_address a
                WHERE partner.id = pc.partner_id
                AND   a.id = pc.address_id
                AND   pc.is_duplicate_detected = TRUE
                AND   pc.active = TRUE

            UNION

                SELECT concat('4.',phc.id) as id,
                       phc.id as orig_id,
                       partner.display_name as partner_name,
                       ph.name as name,
                       'phone.coordinate'::varchar as model,
                       4 as sequence
                FROM  phone_coordinate phc, res_partner partner, phone_phone ph
                WHERE partner.id = phc.partner_id
                AND   ph.id = phc.phone_id
                AND   phc.is_duplicate_detected = TRUE
                AND   phc.active = TRUE

            ORDER BY sequence, partner_name
            )
        """)

# public methods

    def _get_partner_ids(self, cr, uid, context=None):
        """
        Return the partner ids concerned by the duplicate coordinate
        """
        partner_ids = []
        splited = complete_group.split('.')
        if len(splited) != 2:
            raise Warning(_('Should have a correct name of group'))
        module = splited[0]
        group = splited[1]
        model, group_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, module, group)
        configurator_group = self.pool[model].browse(
            cr, uid, [group_id], context=context)[0]
        if configurator_group.users:
            users = configurator_group.users
            partner_ids = [
                u.partner_id.id for u in users
                if u.id != SUPERUSER_ID and u.partner_id.email]
        return partner_ids

    def process_notify_duplicates(
            self, cr, uid, ids=None, force_send=False, context=None):
        """
        Search duplicates and send a summary email to the configurators
        :type force_send: boolean
        :param force_send: If no duplicates found force a mail to say there are
                           no duplicates
        """
        uid = SUPERUSER_ID
        mail_id = False
        partner_ids = self._get_partner_ids(cr, uid, context=context)
        if partner_ids:
            groups = self.read_group(
                cr, uid, [], [], ['model'], context=context,
                orderby='sequence')
            content_text = []
            if groups:
                content_text.append('<p/><table>')
                ir_model = self.pool.get('ir.model')
                for model_domain in [
                        group['__domain'] for group in groups]:
                    model_name = ir_model.search_read(
                        cr,
                        uid,
                        domain=model_domain,
                        fields=['name'],
                        context=context)[0]['name']
                    content_text.append(
                        '<tr><th colspan="2"><br/><u>%s</u></th></tr>' %
                        model_name)
                    duplicates = self.search_read(
                        cr,
                        uid,
                        domain=model_domain,
                        order='name',
                        context=context)
                    for duplicate in duplicates:
                        reason = duplicate['name'] or _(
                            'Unknown birth date')
                        content_text.append(
                            '<tr><td><b>%s</b</td><td>'
                            '<a style="color:blue" href="%s">%s</a></td>'
                            '</tr>' %
                            (duplicate['partner_name'],
                             url.get_document_url(
                                self,
                                cr,
                                uid,
                                duplicate['model'],
                                duplicate['orig_id'],
                                context=context),
                                reason))
                content_text.append('</table><p/>')
            elif force_send:
                content_text.append(
                    '<p>%s</p>' %
                    _('There are no duplicates'))

            if content_text:
                mail_vals = {
                    'subject': _(
                        'Mozaik: Duplicates Summary - %s') %
                    fields.date.today(cr, uid),
                    'body_html': '\n'.join(content_text),
                    'recipient_ids': [[6, False, partner_ids]],
                }
                mail_id = self.pool.get('mail.mail').create(
                    cr,
                    uid,
                    mail_vals,
                    context=context)

        if mail_id:
            _logger.info(
                'process_notify_duplicates: mail id %s created...',
                mail_id)

        return mail_id
