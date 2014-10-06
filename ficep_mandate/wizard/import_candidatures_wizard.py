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

file_import_structure = ['identifier',
                         'partner_name',
                         'is_effective',
                         'list_effective_position',
                         'is_substitute',
                         'list_substitute_position']


class import_sta_candidatures_wizard(orm.TransientModel):
    _name = "import.sta.candidatures.wizard"

    _columns = {
        'selection_committee_id': fields.many2one(
            'sta.selection.committee', string='Selection committee',
            readonly=True, ondelete='cascade'),
        'source_file': fields.binary('Source File'),
        'import_lines': fields.one2many('import.sta.candidatures.file.lines',
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

        committee = self.pool[model].browse(cr, uid, ids[0], context=context)

        res['selection_committee_id'] = committee.id

        return res

    def validate_file(self, cr, uid, ids, context=None):

        wizard = self.browse(cr, uid, ids, context=context)[0]
        source_file = base64.decodestring(wizard.source_file)
        csv_reader = csv.reader(StringIO(source_file))

        line_number = 0
        for data in csv_reader:
            line_number += 1

            if len(data) == 0:
                continue

            if len(data) != len(file_import_structure):
                raise orm.except_orm(_('Error'),
                _('Line %s: a wrong number of columns(%s), %s expected !' %
                  (line_number, len(data), len(file_import_structure))))

            if line_number == 1:
                if data != file_import_structure:
                    raise orm.except_orm(_('Error'),
                    _('Wrong file structure, it should be: %s !' %
                      ','.join(file_import_structure)))
                continue

            identifier = data[file_import_structure.index('identifier')]

            partner_ids = self.pool.get('res.partner').search(cr,
                                                              uid,
                                                              [('identifier',
                                                                '=',
                                                                identifier)])
            if not partner_ids:
                raise orm.except_orm(_('Error'),
                _('Line %s: Partner %s not found in database, \
                   please check source file !' % (line_number, identifier)))
            partner_id = partner_ids[0]

            if not wizard.selection_committee_id.assembly_id.is_legislative:
                if data[file_import_structure.index('is_effective')] == 'True':
                    raise orm.except_orm(_('Error'),
                    _('Line %s: Effective feature is not managed for a \
                      non-legislative assembly !' % line_number))
                if data[
                    file_import_structure.index('is_substitute')
                       ] == 'True':
                    raise orm.except_orm(_('Error'),
                    _('Line %s: Substitute feature is not managed for a \
                      non-legislative assembly !' % line_number))

            values = dict(wizard_id=wizard.id,
                        partner_id=partner_id,
                        partner_name=data[
                                    file_import_structure.index('partner_name')
                                    ] if data[
                                          file_import_structure.index(
                                                            'partner_name')
                                             ] != '' else False,
                        is_effective=data[
                                    file_import_structure.index('is_effective')
                                    ] if data[
                                          file_import_structure.index(
                                                            'is_effective')
                                              ] != '' else False,
                        is_substitute=data[
                                file_import_structure.index('is_substitute')
                                ] if data[file_import_structure.index(
                                                            'is_substitute')
                                          ] != '' else False,
                        list_effective_position=data[
                                file_import_structure.index(
                                                    'list_effective_position')
                                                     ]
                                if data[file_import_structure.index(
                                                    'list_effective_position'
                                                    )] != '' else False,
                        list_substitute_position=data[
                                file_import_structure.index(
                                                    'list_substitute_position')
                                                      ]
                                if data[file_import_structure.index(
                                                    'list_substitute_position')
                                        ] != '' else False,)
            self.pool.get('import.sta.candidatures.file.lines').create(
                                                               cr,
                                                               uid,
                                                               values,
                                                               context=context)

        model, res_id =\
        self.pool.get('ir.model.data').get_object_reference(
                                        cr,
                                        uid,
                                        'ficep_mandate',
                                        'import_sta_candidatures_step2_action')
        action = self.pool[model].read(cr, uid, res_id, context=context)
        action['res_id'] = ids[0]
        action.pop('context', '')
        return action

    def import_candidatures(self, cr, uid, ids, context=None):
        """
        ====================
        import_sta_candidatures
        ====================
        Import candidatures and link them to selection committee
        """
        candidature_pool = self.pool['sta.candidature']

        wizard = self.browse(cr, uid, ids, context=context)[0]

        for line in wizard.import_lines:
            domain = [('selection_committee_id',
                       '=', wizard.selection_committee_id.id),
                      ('partner_id', '=', line.partner_id.id)]
            candidature_ids = candidature_pool.search(cr, uid, domain)

            candidature_values = dict(partner_id=line.partner_id.id,
                        partner_name=line.partner_name,
                        is_effective=line.is_effective,
                        is_substitute=line.is_substitute,
                        list_effective_position=line.list_effective_position\
                                            if line.is_effective else False,
                        list_substitute_position=line.list_substitute_position\
                                            if line.is_substitute else False)

            if candidature_ids:
                candidature_pool.write(cr,
                                       uid,
                                       candidature_ids[0],
                                       candidature_values,
                                       context=context)
            else:
                candidature_values['selection_committee_id'] =\
                                               wizard.selection_committee_id.id
                candidature_pool.create(cr,
                                        uid,
                                        candidature_values,
                                        context=context)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class import_sta_candidature_file_lines (orm.TransientModel):
    _name = "import.sta.candidatures.file.lines"

    _columns = {
        'wizard_id': fields.many2one(
            'import.sta.candidatures.wizard', string='Wizard',
            ondelete='cascade'),
        'partner_id': fields.many2one(
            'res.partner', string='Partner', ondelete='cascade'),
        'partner_name': fields.char('Partner Name', size=128),
        'is_effective': fields.boolean('Effective'),
        'is_substitute': fields.boolean('Substitute'),
        'list_effective_position': fields.integer(
            'Position on effectives list'),
        'list_substitute_position': fields.integer(
            'Position on substitutes list'),
        }
