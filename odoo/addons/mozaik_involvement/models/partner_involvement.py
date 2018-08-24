# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class PartnerInvolvement(models.Model):

    _name = 'partner.involvement'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partner Involvement'
    _rec_name = 'involvement_category_id'
    _order = 'partner_id, id desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        index=True,
        track_visibility='onchange',
        domain=[('is_assembly', '=', False)],
    )
    involvement_category_id = fields.Many2one(
        'partner.involvement.category',
        string='Involvement Category',
        oldname='partner_involvement_category_id',
        required=True,
        index=True,
        track_visibility='onchange',
    )
    note = fields.Text(
        'Notes',
        track_visibility='onchange',
    )
    involvement_type = fields.Selection(
        related='involvement_category_id.involvement_type',
        store=True,
        readonly=True,
        index=True,
    )
    allow_multi = fields.Boolean(
        related='involvement_category_id.allow_multi',
        string='Allow Multiple Involvements',
        store=True,
        readonly=True,
    )
    effective_time = fields.Datetime(
        'Involvement Date',
        copy=False,
        track_visibility='onchange',
    )
    creation_time = fields.Datetime(
        'Involvement Date',
        compute='_compute_creation_time',
        store=True,
    )

    _sql_constraints = [
        (
            'multi_or_not',
            "CHECK (active IS FALSE OR allow_multi IS FALSE OR "
            "involvement_type IN ('donation') OR effective_time IS NOT NULL)",
            'Effective time is mandatory '
            'for this kind of involvement !',
        ),
    ]

    @api.multi
    @api.depends("effective_time")
    def _compute_creation_time(self):
        for involvement in self:
            if involvement.effective_time:
                involvement.creation_time = involvement.effective_time
            else:
                involvement.creation_time = involvement.create_date

    def init(self):
        """
        Create unit indexes based on partner_id and involvement_category_id
        for active records.
        Do not call super() here
        :return:
        """
        cr = self.env.cr

        def create_index(i, index_def):
            createit = True
            query = \
                "SELECT indexdef " \
                "FROM pg_indexes " \
                "WHERE tablename = '%s' AND indexname = '%s_unique_%s_idx'"
            cr.execute(query % (self._table, self._table, i))
            sql_res = cr.dictfetchone()
            if sql_res:
                if sql_res['indexdef'] != index_def:
                    cr.execute(
                        "DROP INDEX %s_unique_%s_idx" % (self._table, i))
                else:
                    createit = False
            if createit:
                cr.execute(index_def)

        index1 = "CREATE UNIQUE INDEX %s_unique_1_idx " \
            "ON %s USING btree " \
            "(partner_id, involvement_category_id) " \
            "WHERE active IS TRUE AND allow_multi IS FALSE" \
            % (self._table, self._table)
        create_index(1, index1)

        index2 = "CREATE UNIQUE INDEX %s_unique_2_idx " \
            "ON %s USING btree " \
            "(partner_id, involvement_category_id, effective_time) " \
            "WHERE active IS TRUE AND allow_multi IS TRUE " \
            "AND (involvement_type NOT IN ('donation') OR " \
            "involvement_type IS NULL)" \
            % (self._table, self._table)
        create_index(2, index2)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        '''
        Add interests to partner when creating an involvement
        Set effective date if any
        '''
        if not vals.get('effective_time'):
            ic = self.env['partner.involvement.category'].browse(
                vals['involvement_category_id'])
            if ic.allow_multi and ic.involvement_type not in ['donation']:
                vals['effective_time'] = fields.Datetime.now()
        res = super(PartnerInvolvement, self).create(vals)
        # terms = res.involvement_category_id.interest_ids
        # if terms:
        #     interests = [
        #         (4, term.id) for term in terms
        #     ]
        #     res.partner_id.suspend_security().write(
        #         {'interest_ids': interests})
        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if self.active and not self.allow_multi:
            raise exceptions.UserError(
                _('An active involvement cannot be duplicated.'))
        res = super(PartnerInvolvement, self).copy(default=default)
        return res

    @api.onchange('allow_multi')
    def _onchange_allow_multi(self):
        if self.allow_multi and self.involvement_type not in ['donation'] \
                and not self.effective_time:
            self.effective_time = fields.Datetime.now()
