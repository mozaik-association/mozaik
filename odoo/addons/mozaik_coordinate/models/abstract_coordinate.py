# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import except_orm

# Available Coordinate Types:
# N/A
COORDINATE_AVAILABLE_TYPES = [
    ('n/a', 'N/A'),
]

coordinate_available_types = dict(COORDINATE_AVAILABLE_TYPES)

MAIN_COORDINATE_ERROR = \
    'Exactly one main coordinate must exist for a given partner'


class AbstractCoordinate(models.Model):

    _name = 'abstract.coordinate'
    _inherit = ['abstract.duplicate']
    _description = 'Abstract Coordinate'

    @api.model
    def _validate_vals(self, vals):
        """
        if no coordinate for this partner then force is_main to true
        """
        domain_other_active_main = self.get_target_domain(
            vals['partner_id'], vals['coordinate_type'])
        coordinate_ids = self.search(domain_other_active_main)
        if not coordinate_ids:
            vals['is_main'] = True
        return

    @api.model
    def _update_magic_numbers(self, magic, new_ids):
        ids = []
        if magic:
            if magic[0][0] == 4:
                ids = [magic[0][1]]
            elif magic[0][0] == 6:
                ids = magic[0][2]
        ids += new_ids
        return [(6, 0, ids)]

    @api.multi
    def _check_force_from(self, email, partner_id):
        if partner_id == self.env.user.patner_id.id:
            return self.with_context(force_from=email)
        return self

    _discriminant_field = None

    # fields

    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        readonly=True, required=True, index=True)
    coordinate_category_id = fields.Many2one(
        'coordinate.category', string='Coordinate Category',
        track_visibility='onchange', index=True)
    coordinate_type = fields.Selection(
        COORDINATE_AVAILABLE_TYPES, 'Coordinate Type', default=COORDINATE_AVAILABLE_TYPES[0][0])
    is_main = fields.Boolean('Is Main', readonly=True, default=False, index=True)
    unauthorized = fields.Boolean(
        'Unauthorized', track_visibility='onchange', default=False)
    vip = fields.Boolean('VIP', track_visibility='onchange', default=False)
    failure_counter = fields.Integer(
        'Failures Counter', track_visibility='onchange', default=0)
    failure_description = fields.Text(
        'Last Failure Description', track_visibility='onchange')
    failure_date = fields.Datetime(
        'Last Failure Date', track_visibility='onchange')

    _order = "partner_id, expire_date, is_main desc, coordinate_type"

    # constraints

    @api.multi
    def _check_one_main_coordinate(self, for_unlink=False):
        """
        ==========================
        _check_one_main_coordinate
        ==========================
        Check if associated partner has exactly one main coordinate
        for a given coordinate type
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        self = self.sudo()  # TODO
        for coordinate in self:
            if for_unlink and not coordinate.is_main:
                continue

            coordinate_ids = self.search(
                [('partner_id', '=', coordinate.partner_id.id),
                 ('coordinate_type', '=', coordinate.coordinate_type)])

            if for_unlink and len(coordinate_ids) > 1 and coordinate.is_main:
                return False

            if not coordinate_ids:
                continue

            coordinate_ids = self.search(
                [('partner_id', '=', coordinate.partner_id.id),
                 ('coordinate_type', '=', coordinate.coordinate_type),
                 ('is_main', '=', True)])
            if len(coordinate_ids) != 1:
                return False

        return True

    _constraints = [
        (_check_one_main_coordinate,
         MAIN_COORDINATE_ERROR, ['partner_id', 'is_main', 'active'])
    ]

    # orm methods

    @api.multi
    def copy_data(self, default=None):
        """
        """
        default = default or {}
        default.update({
            'failure_counter': 0,
            'failure_description': False,
            'failure_date': False,
        })
        res = super().copy_data(default=default)
        return res

    @api.multi
    def name_get(self):
        """
        ========
        name_get
        ========
        :rparam: list of tuple (id, name to display)
                 where id is the id of the object into the relation
                 and display_name, the name of this object.
        :rtype: [(id,name)] list of tuple
        """
        if not self:
            return []


        res = []
        for record in self:
            display_name = self._is_discriminant_m2o() and \
                           record[self._discriminant_field].display_name or \
                           record[self._discriminant_field]
            if self.env.context.get('is_notification', False):
                display_name = '%s: %s' % \
                               (record.partner_id.display_name, display_name) # TODO see [1]?
            res.append((record.id, display_name))
        return res

    @api.model
    def create(self, vals):
        """
        ======
        create
        ======
        When 'is_main' is true the coordinate has to become
        the main coordinate for its associated partner.
        Automatically add the partner as follower of its coordinate
        :rparam: id of the new coordinate
        :rtype: integer

        **Note**
        If new coordinate is main and another main coordinate found into
        the database then the other(s) will not be main anymore
        """
        vals['coordinate_type'] = vals.get('coordinate_type') or \
                                  COORDINATE_AVAILABLE_TYPES[0][0]
        domain_other_active_main = self.get_target_domain(
            vals['partner_id'], vals['coordinate_type'])
        self._validate_vals(vals)
        if vals.get('is_main'):
            mode = self.env.context.get('invalidate') and \
                   'deactivate' or 'secondary'
            validate_fields = self.get_fields_to_update(mode)
            # assure that there are no other main coordinate
            # of this type for this partner
            self_ctx = self
            if self._discriminant_field == 'email':
                self_ctx = self._check_force_from(vals['email'], vals['partner_id'])
            self_ctx.search_and_update(domain_other_active_main, validate_fields)
        # TODO fail when creating new coordinate (don't know yet what _track does exactly)
        # if self._track.get('failure_counter'):
        #     # automatically add the partner as follower of its coordinate
        #     partner_id = vals['partner_id']
        #     message_follower_ids = self._update_magic_numbers(
        #         vals.get('message_follower_ids'), [partner_id])
        #     vals.update({
        #         'message_follower_ids': message_follower_ids,
        #     })
        new_id = super().create(vals)
        if self._track.get('failure_counter'):
            # do not chat with the coordinate owner
            fol_obj = self.env['mail.followers'].sudo()  # TODO
            fol_ids = fol_obj.search([
                ('partner_id', '=', vals['partner_id']),
                ('res_id', '=', new_id.id),
                ('res_model', '=', self._name),
            ])
            if fol_ids:
                imd_obj = self.env['ir.model.data']
                _, discussion_id = imd_obj.get_object_reference('mail', 'mt_comment')
                fol_ids.write({
                    'subtype_ids': [(3, discussion_id)],
                })
        return new_id

    @api.multi
    def unlink(self):
        """
        ======
        unlink
        ======
        :rparam: True
        :rtype: boolean
        :raise: Error if the coordinate is main
                and another coordinate of the same type exists
        """
        coordinates_main = self.filtered(lambda s: s.is_main)
        super(AbstractCoordinate, self - coordinates_main).unlink()
        if not coordinates_main._check_one_main_coordinate(for_unlink=True):
            raise except_orm(_('Error'), _(MAIN_COORDINATE_ERROR))
        res = super(AbstractCoordinate, coordinates_main).unlink()
        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if self.active:
            raise except_orm(
                _('Error'), _('An active coordinate cannot be duplicated!'))
        res = super().copy(default=default)
        return res

    # view methods: onchange, button

    @api.multi
    def button_reset_counter(self):
        """
        Reset the failure counter
        """
        self.write({'failure_counter': 0})

    # public methods

    @api.multi
    def get_linked_partners(self):
        """
        ===================
        get_linked_partners
        ===================
        Returns partner ids linked to coordinate ids
        Path to partner must be object.partner_id
        :rparam: partner_ids
        :rtype: list of ids
        """
        # TODO change where this method is called
        # TODO (remove this method for mapped?)
        # partner_ids = []
        # for record in self:
        #     partner_ids.append(record.partner_id.id)
        # return partner_ids
        return self.mapped("partner_id")

    @api.multi
    def set_as_main(self):
        """
        ===========
        set_as_main
        ===========
        This method allows to switch main coordinate:
        1) Reset is_main of previous main coordinate
        2) Set is_main of new main coordinate
        :rparam: True
        :rtype: boolean
        """
        self.ensure_one()

        # 1) Reset is_main of previous main coordinate
        target_domain = self.get_target_domain(
            self.partner_id.id, self.coordinate_type)
        mode = self.env.context.get('invalidate') and 'deactivate' or 'secondary'
        fields_to_update = self.get_fields_to_update(mode)
        self_ctx = self
        if self._discriminant_field == 'email':
            self_ctx = self._check_force_from(self.email, self.partner_id.id)
        self_ctx.search_and_update(target_domain, fields_to_update)

        # 2) Set is_main of new main coordinate
        res = self.write({'is_main': True})

        return res

    @api.model
    def change_main_coordinate(self, partner_ids, value):
        """
        :param partner_ids: list of partner id
        :type partner_ids: [integer]
        :param value: discriminant field value
        :type value: integer or string
        :rparam: list of created coordinates
        :rtype: list of integer
        """
        return_ids = []
        for partner_id in partner_ids:
            res_ids = self.search([('partner_id', '=', partner_id.id),
                          (self._discriminant_field, '=', value)])
            if not res_ids:
                # create it
                vals = {
                    'partner_id': partner_id.id,
                    self._discriminant_field: value,
                    'is_main': True,
                }
                return_ids.append(self.create(vals))
            else:
                # set it as main if any
                if not res_ids.is_main:
                    res_ids.set_as_main()
        return return_ids

    @api.multi
    def _validate_fields(self, field_names):
        if self.env.context.get('no_check', False):
            return
        super()._validate_fields(field_names)

    @api.model
    def search_and_update(self, target_domain, fields_to_update):
        """
        ==================
        search_and_update
        ==================
        :param target_domain: A domain used into a search
        :type target_domain: list of tuples
        :param fields_to_update: contain the field to be updated
        :type fields_to_update: dictionary
        :rparam: True some objects are found otherwise False
        :rparam: boolean
        **Note**
        1) Search with self on ``target_domain``
        2) Update self with ``fields_to_update``
        """
        res = self.search(target_domain)
        if res:
            res_ctx = res.with_context(no_check=True)
            res_ctx.write(fields_to_update)
        return len(res) != 0

    @api.model
    def get_target_domain(self, partner_id, coordinate_type):
        """
        =================
        get_target_domain
        =================
        :param partner_id: id of the partner
        :type partner_id: integer
        :parma coordinate_type: type of the coordinate
        :type coordinate_type: char
        :rparam: dictionary with ``coordinate_type`` and ``partner_id`` well
        set
        :rtype: dictionary
        """
        return [
            ('partner_id', '=', partner_id),
            ('coordinate_type', '=', coordinate_type),
            ('is_main', '=', True),
        ]

    @api.model
    def get_fields_to_update(self, mode):
        """
        ====================
        get_fields_to_update
        ====================
        :param mode: return a dictionary depending on mode value
        :type mode: char
        """
        res = super().get_fields_to_update(mode)
        if mode == 'main':
            res.update({
                'is_main': True,
            })
        if mode == 'secondary':
            res.update({
                'is_main': False,
            })
        return res

    @api.multi
    def ensure_one_main_coordinate(self, invalidate=False, vals=False):
        '''
            This method ensure that a main coordinate will remain after
            an action
        '''
        limit = 1 if not invalidate else False
        rejected_ids = self.env[self._name]
        for coordinate in self:
            if invalidate:
                domain = ('id', 'not in', self.ids)
            else:
                domain = ('id', '!=', coordinate.id)
            coord_ids = self.search(
                [('partner_id', '=', coordinate.partner_id.id),
                 ('coordinate_type', '=', coordinate.coordinate_type),
                 domain], limit=limit)
            if coordinate.is_main and len(coord_ids) == 1:
                new_main = coord_ids
                coordinate_field = self._discriminant_field
                coordinate_value = self._is_discriminant_m2o() and \
                                   new_main[coordinate_field].id or \
                                   new_main[coordinate_field]
                coordinate_ctx = coordinate.with_context(invalidate=invalidate)
                coordinate_ctx.partner_id.change_main_coordinate(
                    coordinate.partner_id, coordinate_value)
                if vals:
                    coordinate_ctx.write(vals)
            else:
                rejected_ids += coordinate
        return rejected_ids

    @api.multi
    def action_invalidate(self, vals=None):
        rejected_ids = self.ensure_one_main_coordinate(invalidate=True)
        return super(AbstractCoordinate, rejected_ids).action_invalidate(vals=vals)
