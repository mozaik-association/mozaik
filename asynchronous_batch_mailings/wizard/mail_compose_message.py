# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of asynchronous_batch_mailings, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     asynchronous_batch_mailings is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     asynchronous_batch_mailings is distributed in the hope
#     that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with asynchronous_batch_mailings.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp.osv import orm
from openerp.tools.translate import _

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession

_logger = logging.getLogger(__name__)

WORKER_PIVOT = 20
CHUNK_SIZE = 100


class mail_compose_message(orm.TransientModel):

    _inherit = 'mail.compose.message'

    def _prepare_vals(self, vals):
        """
        Remove useless keys and transform all o2m list values with magic number
        """
        for key in ['id', 'notification_ids', 'notified_partner_ids',
                    'child_ids', 'vote_user_ids', ]:
            vals.pop(key, False)
        for key in vals.keys():
            if (isinstance(vals[key], list)):
                vals[key] = [
                    (6, False, vals[key])
                ]

    def send_mail(self, cr, uid, ids, context=None):
        """
        Send mails by asynchronous way depending on parameters
        """
        if context is None:
            context = {}
        if context.get('active_ids'):
            if not context.get('not_async'):
                try:
                    parameter_obj = self.pool['ir.config_parameter']
                    worker_pivot = int(parameter_obj.get_param(
                        cr, uid, 'mail_worker_pivot', WORKER_PIVOT))
                except:
                    worker_pivot = WORKER_PIVOT
                if len(context['active_ids']) > worker_pivot:
                    res_ids = context['active_ids']
                    vals = self.read(
                        cr, uid, ids, [],
                        context=context, load='_classic_write')[0]
                    self._prepare_vals(vals)

                    session = ConnectorSession(cr, uid, context=context)
                    description = _(
                        'Prepare Mailing for "%s" (Chunk Process)'
                        ) % vals['subject']
                    _logger.info(
                        'Delay %s for ids: %s' % (description, res_ids))
                    prepare_mailings.delay(
                        session, self._name, vals, res_ids,
                        description=description, context=context)
                    return {'type': 'ir.actions.act_window_close'}

        return super(mail_compose_message, self).send_mail(
            cr, uid, ids, context=context)


@job
def prepare_mailings(session, model_name, vals, active_ids, context=None):
    self, cr, uid = session, session.cr, session.uid

    ir_param_obj = self.pool['ir.config_parameter']
    chunck_size = ir_param_obj.get_param(cr, uid, 'job_mail_chunck_size',
                                         context=context)

    if not chunck_size.isdigit() or int(chunck_size) < 1:
        chunck_size = CHUNK_SIZE
        _logger.warning('No valid value provided for '
                        '"job_mail_chunck_size" parameter. '
                        'Value %s is used.' % CHUNK_SIZE)

    chunck_size = int(chunck_size)
    chunck_list_active_ids = \
        [active_ids[i:i + chunck_size] for i in range(0, len(active_ids),
                                                      chunck_size)]

    i = 1
    for chunck_active_ids in chunck_list_active_ids:
        description = _('Send Mails "%s" (chunk %s/%s)') %\
            (vals['subject'], i, len(chunck_list_active_ids))
        i = i + 1
        _logger.info(
            'Delay %s for ids: %s' % (description, chunck_active_ids))
        send_mail.delay(
            self, model_name, vals, chunck_active_ids,
            description=description, context=context)


@job
def send_mail(session, model_name, vals, active_ids, context=None):
    do_send_mail(session, model_name, vals, active_ids, context=context)


def do_send_mail(session, model_name, vals, active_ids=None, context=None):
    """
    :param vals: contains the values to create a complete mail_compose_message
        wizard
    :result: send_mail
    """
    context = dict(context or {})
    self, cr, uid = session, session.cr, session.uid
    model = self.pool.get(model_name)
    if active_ids:
        context['active_ids'] = active_ids

    wiz_id = model.create(cr, uid, vals, context=context)
    context['not_async'] = True
    model.send_mail(cr, uid, [wiz_id], context=context)
