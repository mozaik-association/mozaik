# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class VirtualPartnerThesaurusChildSearch(models.AbstractModel):

    _name = "virtual.partner.thesaurus.child.search"

    search_interests_m2m_ids = fields.Many2many(
        compute=lambda s: [],
        comodel_name='thesaurus.term',
        store=False,
        search="_search_interests_m2m_ids")

    search_competencies_m2m_ids = fields.Many2many(
        compute=lambda s: [],
        comodel_name='thesaurus.term', store=False,
        search="_search_competencies_m2m_ids")

    @api.model
    def _search_competencies_m2m_ids(self, operator, value):
        if isinstance(value, str):
            # the user doesn't select a item in the list
            query = """SELECT id FROM thesaurus_term 
            WHERE lower(search_name) 
            LIKE lower(%s); 
            """
            self.env.cr.execute(query, (value, ))
            list_ids = self.env.cr.fetchall()
        else:  # value is a id TODO
            list_ids = []
            pass
        return [('competencies_m2m_ids', 'in', [l[0] for l in list_ids])]

    @api.model
    def _search_interests_m2m_ids(self, operator, value):
        if isinstance(value, str):
            # the user doesn't select a item in the list
            query = """SELECT id FROM thesaurus_term 
            WHERE lower(search_name) 
            LIKE lower(%s); 
            """
            self.env.cr.execute(query, (value, ))
            list_ids = self.env.cr.fetchall()
        else:  # value is a id TODO
            list_ids = []
            pass
        return [('interests_m2m_ids', 'in', [l[0] for l in list_ids])]
