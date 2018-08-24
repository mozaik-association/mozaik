# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2._psycopg import IntegrityError

from odoo.tests import SavepointCase
from odoo.tools.misc import mute_logger


class TestThesaurus(SavepointCase):

    def setUp(self):
        super(TestThesaurus, self).setUp()

        self.thesaurus_model = self.env['thesaurus']

    def test_thesaurus_unique_name(self):
        # already thesaurus see data
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.thesaurus_model.create(
                {'name': 'Thesaurus'})
