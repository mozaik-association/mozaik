# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class VirtualPartnerThesaurusChildSearch(models.AbstractModel):

    _name = "virtual.partner.thesaurus.child.search"

    search_interests_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        store=False,
        search="_search_interests_m2m_ids")

    search_competencies_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term', store=False,
        search="_search_competencies_m2m_ids")

    @api.model
    def _search_competencies_m2m_ids(self, value):
        query = """SELECT * FROM thesaurus_term 
        WHERE lower(search_name) 
        LIKE lower('value%'); 
        """
        query_list_id = self.env.cr.execute(query)
        list_id = query_list_id.fetchall()
        return [('competencies_m2m_ids', 'in', list_id)]

    @api.model
    def _search_interests_m2m_ids(self, value):
        query = """SELECT * FROM thesaurus_term 
        WHERE lower(search_name) 
        LIKE lower('value%'); 
        """
        query_list_id = self.env.cr.execute(query)
        list_id = query_list_id.fetchall()
        return [('interests_m2m_ids', 'in', list_id)]