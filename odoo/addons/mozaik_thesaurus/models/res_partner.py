# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _name = 'res.partner'
    _inherit = ['res.partner', 'abstract.term.finder']
    _terms = ['interests_ids', 'competencies_ids']

    _columns = {
        'competency_ids': fields.many2many(
            'thesaurus.term', 'res_partner_term_competencies_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Competencies', oldname='competencies_m2m_ids'),
        'interest_ids': fields.many2many(
            'thesaurus.term', 'res_partner_term_interests_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Interests', oldname='interests_m2m_ids'),
    }
