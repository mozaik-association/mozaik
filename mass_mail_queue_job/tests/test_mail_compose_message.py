# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.addons.queue_job.job import Job


class TestMailComposeMessage(TransactionCase):

    def _execute_real_job(self, queue_job):
        """
        Load and execute the given queue_job.
        Also refresh the queue_job to have updated fields
        :param queue_job: queue.job recordset
        :return: Job object
        """
        real_job = Job.load(queue_job.env, queue_job.uuid)
        real_job.perform()
        real_job.set_done()
        real_job.store()
        queue_job.refresh()
        return real_job

    def test_mass_send_mail_jobified(self):
        """
        Check for creation of a mail.mail
        from values passed to the wizard.
        """
        # empty jobs queue
        q_model = self.env['queue.job']
        q_model.search([]).unlink()
        # create an attachment
        fname = 'license2kill.doc'
        vals = {
            'datas': 'bWlncmF0aW9uIHRlc3Q=',
            'name': fname,
        }
        attach = self.env['ir.attachment'].create(vals)
        # create a (mass) composer
        subject = 'James Bond: Diamonds are forever'
        vals = {
            'composition_mode': 'mass_mail',
            'body': '<p>sample body</p>',
            'attachment_ids': [[6, 0, [attach.id]]],
            'model': 'res.partner',
            'subject': subject,
        }
        mcm_model = self.env['mail.compose.message'].with_context(
            active_ids=[self.ref('base.res_partner_1')], async_send_mail=True)
        composer = mcm_model.create(vals)
        # execute the composer
        composer.send_mail()
        # get the job
        job = q_model.search([])
        self.assertEqual(1, len(job))
        # try to vacuum composers
        vac_res = mcm_model._transient_vacuum()
        # vacuum has been aborted
        self.assertFalse(vac_res)
        # execute the job
        self._execute_real_job(job)
        self.assertEqual(job.state, 'done')
        # check for the built mail
        mail = self.env['mail.mail'].search([('subject', '=', subject)])
        self.assertEqual(1, len(mail))
        self.assertEqual(1, len(mail.attachment_ids))
        self.assertEqual(fname, mail.attachment_ids.name)
        return
