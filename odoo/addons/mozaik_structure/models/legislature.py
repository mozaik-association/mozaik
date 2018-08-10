# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime as DT

import openerp.tools as tools
from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _


class legislature(orm.Model):

    _name = 'legislature'
    _inherit = ['mozaik.abstract.model']
    _description = 'Legislature'

    _columns = {
        'name': fields.char('Name',
                            size=128,
                            required=True,
                            select=True,
                            track_visibility='onchange'),
        'start_date': fields.date('Start Date',
                                  required=True,
                                  select=True,
                                  track_visibility='onchange'),
        'deadline_date': fields.date('Deadline Date',
                                     required=True,
                                     track_visibility='onchange'),
        'election_date': fields.date('Election Date',
                                     required=True,
                                     track_visibility='onchange'),
        'power_level_id': fields.many2one('sta.power.level',
                                          'Power Level',
                                          required=True,
                                          select=True,
                                          track_visibility='onchange'),
    }

    _order = 'start_date desc, name'

    _unicity_keys = 'power_level_id, name, start_date'

    _sql_constraints = [
        ('date_check1', 'CHECK ( start_date <= deadline_date )',
         'The start date must be anterior to the deadline date.'),
        ('date_check2', 'CHECK ( election_date <= start_date )',
         'The election date must be anterior to the start date.'),
    ]

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        fmt = tools.DEFAULT_SERVER_DATE_FORMAT
        res = []
        for record in self.read(
                cr, uid, ids,
                ['name', 'start_date', 'deadline_date'],
                context=context):
            sdate = DT.datetime.strptime(record['start_date'], fmt)
            edate = DT.datetime.strptime(record['deadline_date'], fmt)
            display_name = '%s (%s-%s)' % \
                (record['name'], sdate.strftime('%Y'), edate.strftime('%Y'))
            res.append((record['id'], display_name))
        return res
