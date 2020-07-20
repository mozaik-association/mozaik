# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_email, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_email is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_email is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_email.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _

from openerp.addons.mozaik_base.base_tools import format_email, check_email


class email_coordinate(orm.Model):

    _name = 'email.coordinate'
    _inherit = ['abstract.coordinate']
    _description = "Email Coordinate"
    _mail_mass_mailing = _('Email Coordinate')

    _track = {
        # specify bounce_date here not bounce_counter to avoid to subscribe
        # the coordinate owner itself (see abstract.create() method)
        'bounce_date': {
            'mozaik_email.email_failure_notification':
                lambda self, cr, uid, obj, ctx=None: obj.bounce_counter,
        },
    }
    _mail_post_access = 'read'

    _discriminant_field = 'email'
    _undo_redirect_action = 'mozaik_email.email_coordinate_action'

    _columns = {
        'email': fields.char('Email', size=100, required=True, select=True),
    }

    _rec_name = _discriminant_field

# constraints

    def _check_email(self, cr, uid, ids, context=None):
        uid = SUPERUSER_ID
        coordinates = self.browse(cr, uid, ids, context=context)
        for coordinate in coordinates:
            if not check_email(coordinate.email):
                return False
        return True

    _constraints = [
        (_check_email, _('Invalid Email Format'), ['email']),
    ]

    _unicity_keys = 'partner_id, email'

# orm methods

    def create(self, cr, uid, vals, context=None):
        """
        ======
        create
        ======
        format email by removing whitespace and changing upper to lower
        """
        if 'email' in vals:
            vals['email'] = format_email(vals['email'])
        return super(email_coordinate, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        format email by removing whitespace and changing upper to lower
        """
        context = context or {}
        if 'email' in vals:
            vals['email'] = format_email(vals['email'])
        return super(email_coordinate, self).write(
            cr, uid, ids, vals, context=context)

    def check_mail_message_access(self, cr, uid, mids, operation,
                                  model_obj=None, context=None):
        if context.get('active_model', False) == 'distribution.list'\
           and (context.get('main_target_model', False) == 'email.coordinate'):
            pass
        else:
            super(email_coordinate, self).check_mail_message_access(
                cr, uid, mids, operation, context=context)

    def update_bounce_counter_mass_mailing(self):
        """
        This method reset the bounce counter on last mailing list
        where no bounce return on coordinate
        """
        # Get mailing lists the period define in the parameters
        check_bounce_date = datetime.today() - timedelta(
            days=int(self.env['ir.config_parameter'].get_param(
                'mozaik_coordinate.bounce_counter_reset_time_delay')))

        query = """
        SELECT mms1.res_id
        FROM mail_mail_statistics AS mms1
        WHERE mms1.bounced IS NOT NULL and mms1.bounced <= %s AND 
        mms1.model = 'email.coordinate' AND  
        mms1.sent < (SELECT mms2.sent
                FROM mail_mail_statistics AS mms2 
                WHERE mms2.bounced IS NULL AND mms2.sent IS NOT NULL AND
                 mms1.res_id = mms2.res_id AND
                 mms2.model = 'email.coordinate' 
                ORDER BY mms2.sent DESC LIMIT 1)
        ORDER BY mms1.sent DESC LIMIT 100
        """
        self.env.cr.execute(query, (datetime.strftime(check_bounce_date, '%Y-%m-%d 23:59:59'),))
        stats = self.env.cr.fetchall()
        self.env["email.coordinate"].browse([s[0] for s in stats]).button_reset_counter()
