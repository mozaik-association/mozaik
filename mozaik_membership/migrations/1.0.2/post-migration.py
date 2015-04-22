# -*- encoding: utf-8 -*-
from openerp.modules.registry import RegistryManager
from openerp.tools import SUPERUSER_ID

__name__ = '''
* Re-Active workflow.instance for dead-end membership' state
* Find membership notification for coordinate and replace it with the right
coordinate bounce notification.
* Find inconsistency between the followers model and the
    message-subtype model and remove concerned values
'''


def migrate(cr, version):
    if not version:
        return
    SQL_QUERY = '''
    UPDATE
        wkf_instance
    SET
        state = 'active'
    WHERE
        res_type = 'res.partner'
        AND
        state = 'complete'
    '''
    cr.execute(SQL_QUERY)
    # bounce and mail_follower notification
    registry = RegistryManager.get(cr.dbname)
    uid = SUPERUSER_ID
    context = registry['res.users'].context_get(cr, uid)
    mail_followers_model = registry['mail.followers']
    xmlid = 'mozaik_membership.membership_line_notification'
    bounce_email_xmlid = 'mozaik_email.email_failure_notification'
    bounce_postal_xmlid = 'mozaik_postal.postal_failure_notification'
    bounce_phone_xmlid = 'mozaik_phone.phone_failure_notification'
    ir_model_data_model = registry['ir.model.data']

    membership_mail_message_subtype_id = ir_model_data_model.xmlid_to_res_id(
        cr, uid, xmlid)
    bounce_email_id = ir_model_data_model.xmlid_to_res_id(
        cr, uid, bounce_email_xmlid)
    bounce_postal_id = ir_model_data_model.xmlid_to_res_id(
        cr, uid, bounce_postal_xmlid)
    bounce_phone_id = ir_model_data_model.xmlid_to_res_id(
        cr, uid, bounce_phone_xmlid)
    models = {
        'email.coordinate': bounce_email_id,
        'postal.coordinate': bounce_postal_id,
        'phone.coordinate': bounce_phone_id,
    }
    for model in models.keys():
        if models[model]:
            domain = [
                ('res_model', '=', model),
                ('subtype_ids', 'in', [membership_mail_message_subtype_id])
            ]
            follower_ids = mail_followers_model.search(
                cr, uid, domain, context=context)
            vals = {
                'subtype_ids': [
                    [3, membership_mail_message_subtype_id],
                    [4, models[model]],
                ]
            }
            mail_followers_model.write(
                cr, uid, follower_ids, vals, context=context)
    SQL_QUERY = '''
    DELETE FROM
        mail_followers_mail_message_subtype_rel r
    USING
        mail_followers mf, mail_message_subtype mms
    WHERE
        mf.id = r.mail_followers_id
        AND
        mms.id = r.mail_message_subtype_id
        AND
        mf.res_model != mms.res_model
    '''
    cr.execute(SQL_QUERY)
