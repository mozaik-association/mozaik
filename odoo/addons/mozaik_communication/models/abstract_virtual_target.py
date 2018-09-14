# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs
from odoo import api, fields, tools, models


class AbstractVirtualTarget(models.AbstractModel):
    """
    Abstract model used to contain common properties for virtual models
    """
    _name = 'abstract.virtual.target'
    _description = 'Abstract Virtual Target'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Partner",
    )
    common_id = fields.Char(
        string="Common ID",
    )
    int_instance_id = fields.Many2one(
        comodel_name='int.instance',
        string='Internal Instance',
    )
    email_coordinate_id = fields.Many2one(
        comodel_name="email.coordinate",
        string="Email coordinate",
    )
    postal_coordinate_id = fields.Many2one(
        comodel_name='postal.coordinate',
        string='Postal Coordinate',
    )
    is_company = fields.Boolean(
        string='Is a Company',
    )
    identifier = fields.Integer(
        string='Number',
        group_operator='min',
    )
    birth_date = fields.Date()
    # Load dynamically selection values
    # If it doesn't work, better way is maybe the related (if selection
    # value come from the related)
    gender = fields.Selection(
        selection=lambda s: s.env['res.partner'].fields_get(
            allfields=['gender']).get('gender', {}).get('selection', [])
    )
    tongue = fields.Selection(
        selection=lambda s: s.env['res.partner'].fields_get(
            allfields=['lang']).get('lang', {}).get('selection', [])
    )
    employee = fields.Boolean()
    competencies_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        string='Competencies',
        related='partner_id.competencies_m2m_ids',
    )
    interests_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        string='Interests',
        related='partner_id.interests_m2m_ids',
    )
    postal_vip = fields.Boolean(
        string='VIP Address',
    )
    postal_unauthorized = fields.Boolean(
        string='Unauthorized Address',
    )
    email_vip = fields.Boolean(
        string="Email VIP",
    )
    email_unauthorized = fields.Boolean(
        string='Unauthorized Email',
    )
    active = fields.Boolean()

    @api.multi
    def get_partner_action(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.partner_id.id,
            'target': 'current',
        }

    @api.model
    def _get_union_parameters(self):
        """
        Get parameters to call this function:
        - _get_query_parameters
        Example, in case of dynamic column name:
        return ['column1', 'column2', ...]
        :return: list
        """
        return []

    @api.model
    def _get_view_name(self):
        """
        Get the name of the view to create
        :return: str
        """
        return self._table

    @api.model
    def _get_query_parameters(self, parameter=False):
        """
        Get dynamic parameters to build the SQL query.
        Parameter is an item given by the _get_union_parameters() function.
        Example: if parameter is 'column1', the type of a specific value
        must be int. But if parameter is 'column2', it should be a string.
        :param parameter: object
        :return: dict
        """
        return {}

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        return ""

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        return ""

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return ""

    @api.model_cr
    def init(self):
        cr = self.env.cr
        view_name = self._get_view_name()
        # To loop at least once, force the [False] if the function return
        # an empty list
        parameters = self._get_union_parameters() or [False]
        sub_queries = []
        for parameter in parameters:
            select_query = self._get_select()
            from_query = self._get_from()
            where_query = self._get_where()
            # Get values to replace into the sub-query
            values = self._get_query_parameters(parameter=parameter)
            sub_query = " ".join([select_query, from_query, where_query])
            # Mogrify return a query string after arguments binding.
            # The string returned is exactly the one that would be sent to the
            # DB after an execute. So the returned string is safe.
            # cfr psycopg official documentation
            sub_queries.append(cr.mogrify(sub_query, values))
        main_query = "\nUNION\n".join(sub_queries)
        tools.drop_view_if_exists(cr, view_name)
        query = """CREATE OR REPLACE VIEW %(table_name)s AS (
                        SELECT *, row_number() AS id
                        FROM (%(main_query)s));"""
        main_values = {
            "table_name": AsIs(view_name),
            "main_query": AsIs(main_query),
        }
        cr.execute(query, main_values)
