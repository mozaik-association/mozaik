# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, SUPERUSER_ID


class mail_compose_message(orm.TransientModel):

    _inherit = 'mail.compose.message'

    _columns = {
        'contact_ab_pc': fields.integer(),
    }

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        """
        If the wizard's model is `email.coordinate` then the recipient is the
        email of the `email.coordinate`
        """
        values = super(mail_compose_message, self).get_mail_values(
            cr, uid, wizard, res_ids, context=context)
        mailing_ids = set(r['mailing_id']
                          for r in values.itervalues()
                          if r.get('mailing_id'))
        if mailing_ids:
            mailing_values = {
                'contact_ab_pc': wizard.contact_ab_pc,
            }
            if context.get('mailing_group_id'):
                mailing_values['group_id'] = context['mailing_group_id']
            self.pool['mail.mass_mailing'].write(
                cr, uid, list(mailing_ids), mailing_values, context=context)
        email_path = context.get('email_coordinate_path', False)
        if email_path:
            for model_obj in self.pool[wizard.model].browse(
                    cr, SUPERUSER_ID, values.keys(), context=context):
                email = eval('%s.%s' % ('model_obj', email_path))
                if email:
                    values[model_obj['id']].pop('recipient_ids', [])
                    values[model_obj['id']]['email_to'] = email
        return values

    def _transient_vacuum(self, cr, uid, force=False):
        """
        Do not unlink mail composer wizards if unfinished jobs exist
        """
        res = True
        domain = [('state', '!=', 'done')]
        job_ids = self.pool['queue.job'].search(cr, uid, domain)
        if not job_ids:
            res = super(mail_compose_message, self)._transient_vacuum(
                cr, uid, force=force)
        return res

    def send_mail(self, cr, uid, ids, context=None):
        """
        Do not recompute ids if sending mails asynchronously
        """
        context = context or {}
        if not context.get('async_send_mail'):
            context = dict(context, dl_computed=True)
        return super(mail_compose_message, self).send_mail(
            cr, uid, ids, context=context)
