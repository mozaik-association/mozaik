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
import base64
from csv import reader
import tempfile
import logging

from openerp import fields, api, models
from openerp.tools.translate import _
from openerp.exceptions import Warning
_logger = logging.getLogger(__name__)


class FileTermsLoader(models.TransientModel):

    _name = 'thesaurus.terms.loader'
    _description = 'Thesaurus Terms Loader'

    file_terms = fields.Binary(string='File to Load', required=True)

    @api.multi
    def _get_tmp_file(self):
        self.ensure_one()
        tmp = tempfile.NamedTemporaryFile(
            prefix='ImportTerms', suffix='.csv', delete=False)
        tmp.write(base64.decodestring(self.file_terms))
        tmp.close()
        return tmp

    @api.multi
    def _get_data(self):
        self.ensure_one()
        tmp_file = self._get_tmp_file()
        datas = []
        try:
            f = open(tmp_file.name, 'rt')
            f_reader = reader(f, delimiter=';')
            for row in f_reader:
                datas.append(row)
            f.close()
        except Exception as e:
            _logger.error(e.message)
            raise Warning(_('Thesaurus file is not well formed'))

        return datas

    @api.model
    def _update_terms(
            self, datas, to_update_identifiers):
        """
        If the value of the identifiers'id is not the same than the value of
        the thesaurus_term_id found with the identifier
        then update it with the value into datas for
        this external identifier
        :type datas: dict
        :param datas: contains the value to update per ext_identifier
        :type to_update_identifiers: [int]
        :param to_update_identifiers: list of identifiers that are here to be
            updated or not
        :rtype: integer
        :rparam: number of updated records
        """
        cpt = 0
        for identifier in to_update_identifiers:
            domain = [('ext_identifier', '=', identifier)]
            t_term_id = self.env['thesaurus.term'].search(domain)
            data_name = datas[identifier]['name'].decode('UTF-8')
            if data_name != t_term_id.name:
                t_term_id.name = data_name
                cpt += 1
        return cpt

    @api.model
    def _create_terms(
            self, datas, to_create_identifiers):
        """
        Create a thesaurus term for each to_create_identifiers with the value
        associated to th identifiers into datas
        :type datas: dict
        :param datas: contains the value for the create
        :type to_create_identifiers: [int]
        :param to_create_identifiers: list of identifiers that are here to be
            created
        :rtype: integer
        :rparam: number of created records
        """
        ids = []
        for identifier in to_create_identifiers:
            vals = dict(datas[identifier], state='confirm')
            vals.pop('relations')
            ids.append(self.env['thesaurus.term'].create(vals))
        return len(ids)

    @api.model
    def _get_data_by_external_identifier(self):
        # as the file should not be too large we temporary save the content
        # into datas_file
        datas_file = self._get_data()
        identifier_datas = {}
        keys = ['ext_identifier', 'name', 'relations']
        dict_datas = [dict(zip(keys, values)) for values in datas_file]
        for dict_data in dict_datas:
            identifier_datas[dict_data[keys[0]]] = dict_data
        return identifier_datas

    @api.model
    def cu_terms(self, identifier_datas):
        """
        :type datas_file: {}
        :param datas_file:
        {'ext_identifier': {'ext_identifier', 'name', 'parent_ext_ids'}}
        """
        ext_identifiers = identifier_datas.keys()
        thesaurus_term_ids = self.env['thesaurus.term'].sudo().search([])
        existing_identifiers = [t.ext_identifier for t in thesaurus_term_ids]

        to_update_identifiers =\
            list(set(ext_identifiers) & set(existing_identifiers))
        nb_to_update = len(to_update_identifiers)
        if nb_to_update:
            _logger.info(
                'Start Updating %d Existing Terms' % len(
                    to_update_identifiers))
            nb_updated = self._update_terms(
                identifier_datas, to_update_identifiers)
            _logger.info('%d/%d Updated' % (nb_updated, nb_to_update))

        to_create_identifiers =\
            list(set(ext_identifiers) - set(existing_identifiers))
        nb_to_create = len(to_create_identifiers)
        if nb_to_create:
            _logger.info(
                'Start Creating %d New Terms' % len(to_create_identifiers))
            nb_created = self._create_terms(
                identifier_datas, to_create_identifiers)
            _logger.info(
                '%d/%d New Terms Created' % (nb_created, nb_to_create))

    @api.model
    def set_relation_terms(self, identifier_datas):
        """
        Set the parent/children depending of the identifier_datas
        Launch the compute of the search name once the work is done
        :type identifier_datas: {}
        :param identifier_datas:
        {'ext_identifier': {'ext_identifier', 'name', 'parent_ext_ids'}}
        """
        t_t_model = self.env['thesaurus.term']
        for identifier in identifier_datas.keys():
            ext_relations_ids = identifier_datas[identifier]['relations']
            if ext_relations_ids:
                ext_relations_ids = ext_relations_ids.split(',')
                ext_relations_ids.append(identifier)
                domain = [
                    ('ext_identifier', 'in', ext_relations_ids)
                ]
                term_ids = t_t_model.search(domain)
                if len(term_ids) > 1:
                    main_term = term_ids.filtered(
                        lambda t: t.ext_identifier == identifier)
                    parent_term_ids = term_ids.filtered(
                        lambda t: t.ext_identifier != identifier).ids
                    main_term.set_relation_terms(parent_term_ids)
        t_t_model.search([]).compute_search_name()

    @api.multi
    def load_terms(self):
        """
        * Read file
        * Create terms with col1 & col2
        * Reset relation with col1, col3a,col3b,col3c
        """
        self.ensure_one()
        _logger.info('Start loading terms...')
        identifier_datas = self._get_data_by_external_identifier()
        _logger.info('Start Creating/Updating Terms')
        self.cu_terms(identifier_datas)
        _logger.info('Start Updating Relations between Terms')
        self.set_relation_terms(identifier_datas)
        _logger.info('Relations between Terms Updated')
