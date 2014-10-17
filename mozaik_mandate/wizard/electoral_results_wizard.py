# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields
from openerp.tools.translate import _
import base64
import csv
from StringIO import StringIO

file_import_structure = ['district',
                         'E/S',
                         'name',
                         'votes',
                         'position',
                         'position_non_elected']

file_errors = {
    'LINE_SIZE': _('')
}


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class electoral_results_wizard(orm.TransientModel):
    _name = "electoral.results.wizard"

    _columns = {
        'legislature_id': fields.many2one('legislature',
                                          string='Legislature',),
        'source_file': fields.binary('Source File'),
        'error_lines': fields.one2many('electoral.results.wizard.errors',
                                        'wizard_id',
                                        'Errors'),
        'file_lines': fields.one2many('electoral.results.wizard.lines',
                                        'wizard_id',
                                        'File lines'),
        }

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        res = {}
        context = context or {}

        model = context.get('active_model', False)
        if not model:
            return res

        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []

        legislature = self.pool[model].browse(cr, uid, ids[0], context=context)
        res['legislature_id'] = legislature.id

        return res

    def validate_file(self, cr, uid, ids, context=None):
        def save_error():
            error_obj.create(cr, uid,
                                 {'wizard_id': wizard.id,
                                  'line_number': line_number,
                                  'error_msg': error_msg})
        district_obj = self.pool.get('electoral.district')
        candi_obj = self.pool.get('sta.candidature')
        error_obj = self.pool.get('electoral.results.wizard.errors')
        line_obj = self.pool.get('electoral.results.wizard.lines')
        wizard = self.browse(cr, uid, ids, context=context)[0]
        source_file = base64.decodestring(wizard.source_file)
        csv_reader = csv.reader(StringIO(source_file))
        known_districts = {}

        line_number = 0
        for line in csv_reader:
            line_number += 1
            error_msg = False
            if line == '':
                continue

            if len(line) != len(file_import_structure):
                error_msg = _('Wrong number of columns(%s), '\
                            '%s expected !' % (len(line),
                                               len(file_import_structure)))
                save_error()
                continue

            if line_number == 1:
                continue

            district = line[0]
            e_s = line[1]
            name = line[2]
            votes = line[3]
            position = line[4]
            position_non_elected = line[5]

            if not is_integer(votes):
                error_msg = _('Votes value should be integer: %s' %
                              votes)
                save_error()
                continue

            if position:
                if not is_integer(position):
                    error_msg = _('Position value should be integer: %s' %
                                  position)
                    save_error()
                    continue

            if position_non_elected:
                if not is_integer(position_non_elected):
                    error_msg = _('Position non elected value should '\
                                  'be integer: %s' % position_non_elected)
                    save_error()
                    continue

            district_id = False
            if district not in known_districts:
                district_id = district_obj.search(cr, uid,
                                    [('name', '=', district)],
                                    limit=1,
                                    context=context)
                if not district_id:
                    error_msg = _('Unknown district: %s' %
                                  district)
                    save_error()
                    continue
                else:
                    known_districts[name] = district_id[0]

            candidature_ids = candi_obj.search(cr, uid,
                                              [('partner_name',
                                                '=',
                                                name),
                                               ('electoral_district_id',
                                                '=',
                                                district_id[0]),
                                               ('legislature_id',
                                                '=',
                                                wizard.legislature_id.id),
                                               ('active', '<=', True)],
                                              limit=1,
                                              context=context)

            if not candidature_ids:
                    error_msg = _('Unknown candidate: %s' %
                                  name)
                    save_error()
                    continue

            candidature = candi_obj.browse(cr, uid, candidature_ids[0],
                                           context=context)

            if not e_s:
                if candidature.is_effective or candidature.is_substitute:
                    value = 'E' if candidature.is_effective else 'S'
                    error_msg = _('Candidature: inconsistent value for '\
                                   'column E/S: should be %s' % value)
                    save_error()
                    continue
                if position and position_non_elected:
                    value = 'E' if candidature.is_effective else 'S'
                    error_msg = _('Position(%s) and position non elected(%s)'
                                  ' can not be set both' %
                                  (position, position_non_elected))
                    save_error()
                    continue

            elif e_s == 'E':
                if not candidature.is_effective:
                    error_msg = _('Candidature is not flagged as effective')
                    save_error()
                    continue

            elif e_s == 'S':
                if not candidature.is_substitute:
                    error_msg = _('Candidature is not flagged as substitute')
                    save_error()
                    continue
            else:
                error_msg = _('Inconsistent value for column E/S: %s' % e_s)
                save_error()
                continue

            if e_s and position_non_elected:
                error_msg = _('Position non elected is incompatible'\
                              ' with e_s value: %s' % e_s)
                save_error()
                continue

            if candidature.state == 'designated':
                pass
            elif candidature.state == 'elected':
                if position_non_elected > 0:
                    error_msg = _('Candidature is elected but position '\
                                  'non elected (%s) is set' %
                                  position_non_elected)
                    save_error()
                    continue
            elif candidature.state == 'non-elected':
                pass
            else:
                error_msg = _('Inconsistent state for candidature: %s ' %
                              candidature.state)
                save_error()
                continue

            line_obj.create(cr, uid, {'wizard_id': wizard.id,
                                      'sta_candidature_id': candidature.id,
                                      'data': str(line)},
                            context=context)

        model, res_id =\
        self.pool.get('ir.model.data').get_object_reference(
                                    cr,
                                    uid,
                                    'mozaik_mandate',
                                    'electoral_results_wizard_step2_action')
        action = self.pool[model].read(cr, uid, res_id, context=context)
        action['res_id'] = ids[0]
        action.pop('context', '')
        return action

    def import_file(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids, context=context)[0]

        for line in wizard.file_lines:
            candi_obj = self.pool.get('sta.candidature')
            file_line = eval(line.data)

            e_s = file_line[1]
            votes = file_line[3]
            position = file_line[4]
            position_non_elected = file_line[5]

            position_col = 'election_effective_position'
            votes_col = 'effective_votes'

            signal = 'button_elected'

            if not e_s and position_non_elected:
                position = position_non_elected
                e_s = 'S'

            if e_s == 'S':
                position_col = 'election_substitute_position'
                votes_col = 'substitute_votes'
                if not line.sta_candidature_id.is_effective:
                    signal = 'button_non_elected'
                else:
                    signal = False

            if e_s == 'E':
                if not position or int(position) == 0:
                    signal = 'button_non_elected'

            vals = {position_col: position,
                    votes_col: votes}

            candi_obj.write(cr, uid,
                            line.sta_candidature_id.id, vals, context=context)

            if line.sta_candidature_id.state == 'designated' and signal:
                candi_obj.signal_workflow(cr,
                                          uid,
                                          [line.sta_candidature_id.id],
                                          signal, context=context)


class electoral_results_wizard_errors(orm.TransientModel):
    _name = "electoral.results.wizard.errors"

    _columns = {
        'wizard_id': fields.many2one('electoral.results.wizard',
                                          string='Wizard'),
        'line_number': fields.integer('Line Number'),
        'error_msg': fields.text('Message')
    }


class electoral_results_wizard_lines(orm.TransientModel):
    _name = "electoral.results.wizard.lines"

    _columns = {
        'wizard_id': fields.many2one('electoral.results.wizard',
                                          string='Wizard'),
        'sta_candidature_id': fields.many2one('sta.candidature',
                                          string='Candidature'),
        'data': fields.text('File values')
    }
