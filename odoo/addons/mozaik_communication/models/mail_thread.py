# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def get_first_text_part(self, msg):
        """

        :param msg:
        :return:
        """
        maintype = msg.get_content_maintype()
        if maintype == 'multipart':
            for part in msg.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
                if part.get_content_maintype() == 'multipart':
                    return get_first_text_part(part)
        elif maintype == 'text':
            return msg.get_payload()

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None,
                      custom_values=None):
        """
        Prepare a new context with the bounce body allowing to post it later
        on the faulty email coordinate in case the received message is a bounce
        :param message: Message object
        :param message_dict: dict
        :param model: str
        :param thread_id: int
        :param custom_values: dict
        :return: list of routes
                [(model, thread_id, custom_values, user_id, alias)]
        """
        bounce_body = self.get_first_text_part(message)
        return super(MailThread, self.with_context(
            bounce_body=bounce_body)).message_route(
            message=message, message_dict=message_dict, model=model,
            thread_id=thread_id, custom_values=custom_values)
