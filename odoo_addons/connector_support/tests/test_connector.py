# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.addons.connector.queue.job import (
    Job,
    OpenERPJobStorage,
)
from openerp.addons.connector.session import (
    ConnectorSession,
)


def sample_job(session, model_name):
    """
    Sample job
    """


class TestConnector(TransactionCase):

    def setUp(self):
        super(TestConnector, self).setUp()
        self.session = ConnectorSession(self.cr, self.uid)

    def _create_job(self):
        test_job = Job(func=sample_job)
        storage = OpenERPJobStorage(self.session)
        storage.store(test_job)
        stored = storage.db_record_from_uuid(test_job.uuid)
        return stored

    def test_subscribe_users(self):
        group = self.env.ref('connector_support.group_connector_support')
        stored = self._create_job()
        followers = stored.message_follower_ids
        self.assertFalse(
            set(group.users.mapped('partner_id')) - set(followers))
