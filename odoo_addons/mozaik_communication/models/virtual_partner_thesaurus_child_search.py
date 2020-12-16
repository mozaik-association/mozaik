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
            WHERE lower(name)
            LIKE lower(%s); 
            """
            self.env.cr.execute(query, (value, ))
            term_id = self.env.cr.fetchone()
            if term_id is not None:
                value = term_id[0]
        if isinstance(value, int):
            query = """WITH RECURSIVE c AS (
               SELECT %s as stc FROM public.child_term_parent_term_rel
               UNION
               SELECT sa.child_term_id
               FROM public.child_term_parent_term_rel AS sa
               JOIN c ON c.stc = sa.parent_term_id
            )
            SELECT * FROM c ORDER BY stc ASC ;"""
            self.env.cr.execute(query, (value,))
            list_ids = self.env.cr.fetchall()
        else:
            list_ids = []
        return [('competencies_m2m_ids', 'in', [l[0] for l in list_ids])]

    @api.model
    def _search_interests_m2m_ids(self, operator, value):
        if isinstance(value, str):
            # the user doesn't select a item in the list
            query = """SELECT id FROM thesaurus_term
            WHERE lower(name) 
            LIKE lower(%s); 
            """
            self.env.cr.execute(query, (value, ))
            term_id = self.env.cr.fetchone()
            if term_id is not None:
                value = term_id[0]
        if isinstance(value, int):
            query = """WITH RECURSIVE c AS (
               SELECT %s as stc FROM public.child_term_parent_term_rel
               UNION
               SELECT sa.child_term_id
               FROM public.child_term_parent_term_rel AS sa
               JOIN c ON c.stc = sa.parent_term_id
            )
            SELECT * FROM c ORDER BY stc ASC ;"""
            self.env.cr.execute(query, (value,))
            list_ids = self.env.cr.fetchall()
        else:
            list_ids = []
        return [('interests_m2m_ids', 'in', [l[0] for l in list_ids])]
