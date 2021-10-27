# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs
from odoo import api, fields, tools, models


class AbstractVirtualModel(models.AbstractModel):
    """
    Abstract model used to contain common properties for virtual models
    """
    _name = 'abstract.virtual.model'
    _description = 'Abstract Virtual Model'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Partner",
    )
    common_id = fields.Char(
        string="Common ID",
    )
    result_id = fields.Many2one(
        comodel_name='virtual.target',
        string='Result',
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
    lang = fields.Selection(
        string='Language',
        selection=lambda s: s.env['res.partner'].fields_get(
            allfields=['lang']).get('lang', {}).get('selection', [])
    )
    employee = fields.Boolean()
    competency_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        string='Competencies',
        related='partner_id.competency_ids',
    )
    interest_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        string='Interests',
        related='partner_id.interest_ids',
    )
    partner_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string='Partner Internal Instances',
        related='partner_id.int_instance_ids',
    )
    active = fields.Boolean()

    # search field
    int_instance_id = fields.Many2one(
        comodel_name='int.instance',
        string='Internal Instance',
        store=False,
        search='_search_int_instance_id',
    )

    @api.model
    def _search_int_instance_id(self, operator, value):
        """
        Use partner_instance_ids to search on int_instance_id
        """
        instance_mod = self.env['int.instance']
        if isinstance(value, (int, list)):
            instances = instance_mod.search([('id', operator, value)])
        else:
            instances = instance_mod.search([('name', operator, value)])
        return [('partner_instance_ids', 'in', instances.ids)]

    def see_partner_action(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
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
        select = """SELECT
            p.id AS common_id,
            p.id AS partner_id,
            p.is_company AS is_company,
            p.identifier AS identifier,
            p.birthdate_date AS birth_date,
            p.gender AS gender,
            p.lang AS lang,
            p.employee AS employee,
            CASE
                WHEN (p.email IS NOT NULL OR p.address_address_id IS NOT NULL)
                THEN True
                ELSE False
            END AS active"""
        return select

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

    @api.model
    def _select_virtual_target(self):
        return """
            ,vt.id AS result_id
        """

    @api.model
    def _from_virtual_target(self):
        return """
        LEFT OUTER JOIN
            virtual_target as vt
        ON
            vt.partner_id = p.id
            """

    def init(self):
        if self._abstract:
            return
        cr = self.env.cr
        view_name = self._get_view_name()
        # To loop at least once, force the [False] if the function return
        # an empty list
        parameters = self._get_union_parameters() or [False]
        sub_queries = []
        for parameter in parameters:
            select_query = "%s %s" % (self._get_select(),
                                      self._select_virtual_target())
            from_query = "%s %s" % (self._get_from(),
                                    self._from_virtual_target())
            where_query = self._get_where()
            # Get values to replace into the sub-query
            values = self._get_query_parameters(parameter=parameter)
            sub_query = " ".join([select_query, from_query, where_query])
            # Mogrify return a query string after arguments binding.
            # The string returned is exactly the one that would be sent to the
            # DB after an execute. So the returned string is safe.
            # cfr psycopg official documentation
            sub_queries.append(cr.mogrify(sub_query, values).decode('utf-8'))
        main_query = " \nUNION\n ".join(sub_queries)
        tools.drop_view_if_exists(cr, view_name)
        query = """CREATE OR REPLACE VIEW %(table_name)s AS (
            SELECT
                e.*, row_number() OVER(ORDER BY
                    %(order_by)s
                ) AS id
            FROM (%(main_query)s) AS e);"""
        main_values = {
            "table_name": AsIs(view_name),
            "main_query": AsIs(main_query),
            "order_by": AsIs(self._get_order_by()),
        }
        cr.execute(query, main_values)

    @api.model
    def _get_order_by(self):
        return "partner_id"
