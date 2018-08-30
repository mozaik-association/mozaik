# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _
from odoo.addons.mozaik_tools.tools import format_value


class ResPartner(models.Model):

    _name = 'res.partner'
    _inherit = ['abstract.duplicate', 'res.partner']

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

    _discriminant_field = 'name'
    _trigger_fields = ['active', 'name', 'birthdate_date']
    _undo_redirect_action = 'contacts.action_contacts'
    _order = 'select_name'
    _unicity_keys = 'N/A'

    identifier = fields.Integer(
        'Number',
        index=True,
        copy=False,
        default=False,
        group_operator='min',
    )
    acronym = fields.Char(
        track_visibility='onchange',
    )
    select_name = fields.Char(
        compute='_compute_names',
        store=True,
        index=True,
    )
    technical_name = fields.Char(
        compute='_compute_names',
        store=True,
        index=True,
    )
    printable_name = fields.Char(
        compute='_compute_names',
        store=True,
        index=True,
    )

    # complete existing fields
    firstname = fields.Char(
        track_visibility='onchange',
    )
    lastname = fields.Char(
        track_visibility='onchange',
    )
    usual_firstname = fields.Char(
        track_visibility='onchange',
    )
    usual_lastname = fields.Char(
        track_visibility='onchange',
    )

    @api.depends(
        'is_company', 'name', 'parent_id.name', 'type', 'company_name',
        'identifier', 'select_name')
    def _compute_display_name(self):
        return super()._compute_display_name()

    @api.multi
    @api.depends(
        'is_company', 'acronym', 'identifier', 'name', 'usual_name',
        'firstname', 'lastname', 'usual_firstname', 'usual_lastname')
    def _compute_names(self):
        """
        Compute derived names from firstname and lastname
        """
        for partner in self:
            if partner.is_company:
                s_name = p_name = partner.name
                if partner.acronym:
                    s_name = "%s (%s)" % (partner.name, partner.acronym)
            else:
                s_name = partner.usual_name
                if s_name != partner.name:
                    s_name = "%s (%s)" % (s_name, partner.name)
                names = partner._get_names(usual=True, reverse=True)
                p_name = partner._get_computed_name(names[0], names[1])

            partner.select_name = s_name
            partner.technical_name = format_value(s_name, remove_blanks=True)
            partner.printable_name = p_name

    @api.multi
    @api.constrains('identifier')
    def _check_identifier(self):
        """
        Check if identifier is unique
        """
        partners = self.filtered(lambda s: s.identifier)
        identifiers = partners.mapped('identifier')
        if not identifiers:
            return
        other = self.env['res.partner'].sudo().search([
            ('identifier', 'in', identifiers)])
        for partner in partners:
            p = other.filtered(
                lambda s, p=partner: s != p and s.identifier == p.identifier)
            if p:
                raise exceptions.ValidationError(
                    _('Identifier %s is already assigned') %
                    partner.identifier)

    @api.model
    def _get_duplicates(self, value):
        """
        Get duplicates
        * If one of these duplicates has no ``birthdate_date`` return all
          duplicates
        * Otherwise return duplicates with the same ``birthdate_date``
          and reset all others
        :param value: discriminant field value
        :return: self recordset
        """
        duplicates = super()._get_duplicates(value)
        if duplicates.filtered(lambda s: not s.birthdate_date):
            return duplicates

        detected_duplicates = self.browse()
        if duplicates:
            # group duplicates by birth date
            dates = duplicates.mapped('birthdate_date')
            duplicates_by_date = {d: self.browse() for d in dates}
            for duplicate in duplicates:
                duplicates_by_date[duplicate.birthdate_date] |= duplicate
            # all groups of size > 1 are real duplicates
            # all groups of size = 1 are false duplicates
            false_duplicates = self.browse()
            for grp in duplicates_by_date.values():
                if len(grp) > 1:
                    detected_duplicates |= grp
                else:
                    false_duplicates |= grp
            # reset false duplicates
            false_duplicates = false_duplicates.filtered(
                lambda s: s.is_duplicate_allowed or
                s.is_duplicate_detected)
            if false_duplicates:
                values_write = self._get_fields_to_update('reset')
                false_duplicates.with_context(escape_detection=True).write(
                    values_write)
        return detected_duplicates

    @api.multi
    def name_get(self):
        """
        Add identifier to name_get result
        """
        result = res = super().name_get()
        if not any([
                self._context.get('show_address_only'),
                self._context.get('show_address'),
                self._context.get('show_email')]):
            p_dict = {p.id: p for p in self}
            result = []
            for rec in res:
                identifier = p_dict[rec[0]].identifier
                if identifier:
                    result.append(
                        (rec[0], '%s-%s' % (
                            identifier, p_dict[rec[0]].select_name)))
                else:
                    result.append(
                        (rec[0], p_dict[rec[0]].select_name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            op = operator if operator in ['like', 'ilike', '=', ] else 'ilike'
            ident = int(name) if name.isdigit() else -1
            domain = [
                '|', '|',
                ('select_name', op, name),
                ('technical_name', op, name),
                ('identifier', '=', ident),
            ]
        partners = self.search(domain + args, limit=limit)
        return partners.name_get()

    @api.model
    def create(self, vals):
        """
        Add an identifier from a sequence if any
        """
        if vals.get('is_assembly'):
            vals.pop('identifier')
        if not vals.get('is_assembly') and not vals.get('identifier'):
            vals['identifier'] = self.env['ir.sequence'].next_by_code(
                'res.partner')

        res = super().create(vals)
        return res

    @api.multi
    def _create_user(self, login, group_ids):
        """
        Create a user from an existing partner
        :param login: char
        :param group_ids: recordset
        :raise: if partner is already a user or is a company or is inactive
        :return: the user
        """
        self.ensure_one()

        if self.user_ids:
            raise exceptions.UserError(
                _('%s is already a user!') % self.display_name)

        if self.is_company and not self.is_assembly:
            raise exceptions.UserError(
                _('%s cannot be a company to become a user!') %
                self.display_name)

        if not self.active:
            raise exceptions.UserError(
                _('%s must be active to become a user!') % self.display_name)

        vals = {'groups_id': [(6, 0, group_ids.ids)]} if group_ids else {}
        vals.update({
            'partner_id': self.id,
            'login': login,
        })

        user = self.env['res.users'].with_context(
            no_reset_password=True).create(vals)

        return user

    @api.model
    def _update_identifier_sequence(self):
        """
        Update next value (after data migration) of identifier sequence
        """
        self.env.cr.execute("""
            SELECT MAX(identifier) + 1
            FROM res_partner""")
        next_value = self.env.cr.fetchone()[0] or 1
        seq = self.env.ref('mozaik_person.res_partner_identifier_sequence')
        seq.number_next = next_value
