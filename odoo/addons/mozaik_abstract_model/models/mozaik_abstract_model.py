# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from psycopg2.extensions import AsIs
from psycopg2 import IntegrityError
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MozaikAbstractModel(models.AbstractModel):
    _name = 'mozaik.abstract.model'
    _inherit = ['mail.thread']
    _description = 'Mozaik abstract model'

    _allowed_inactive_link_models = []
    _inactive_cascade = False
    _unicity_keys = None

    expire_date = fields.Datetime(
        'Expiration Date',
        readonly=True,
        default=False,
        track_visibility='onchange',
        copy=False,
    )
    active = fields.Boolean(
        default=True,
        copy=False,
    )

    # magic field
    create_date = fields.Datetime(
        readonly=True,
    )

    @api.model
    def _get_index_name(self):
        """
        Get the dynamic index/constraint name
        :return: str
        """
        return "%s_unique_idx" % self._table

    def init(self):
        """
        Create unique index based on models who implements this abstract model
        """
        result = super().init()

        if not self._auto or self._abstract:
            return result

        create_index = True
        drop_index = False
        if self._unicity_keys == 'N/A':
            drop_index = True
            create_index = False

        if not self._unicity_keys:
            _logger.warning('No _unicity_keys specified for model %s',
                            self._name)
            drop_index = True
            create_index = False

        cr = self.env.cr
        unicity = " ".join(self._unicity_keys.split())
        index_name = self._get_index_name()
        index_query = "CREATE UNIQUE INDEX %(index_name)s ON %(table_name)s " \
                      "USING btree (%(btree)s) WHERE (active IS TRUE)"
        index_values = {
            "index_name": AsIs(index_name),
            "table_name": AsIs(self._table),
            "btree": AsIs(unicity),
        }
        query = "SELECT indexdef " \
                "FROM pg_indexes " \
                "WHERE tablename = %(table_name)s " \
                "AND indexname = %(index_name)s;"
        query_values = {
            "index_name": index_name,
            "table_name": self._table,
        }
        cr.execute(query, query_values)
        sql_res = cr.dictfetchone()
        if sql_res:
            previous = sql_res.get('indexdef', '').replace(
                ' ON public.', ' ON ')
            if previous != index_query % index_values:
                _logger.info(
                    'Rebuild index %s_unique_idx:\n%s\n%s',
                    self._name, previous, index_query)
                drop_index = True
            else:
                create_index = False
        else:
            drop_index = False

        if drop_index:
            drop_values = {
                "index_name": AsIs(index_name),
            }
            cr.execute("DROP INDEX %(index_name)s;", drop_values)

        if create_index:
            cr.execute(index_query, index_values)
        return result

    @api.model
    def _get_exception_messages(self):
        """
        Build a dict where the key is the constraint name (index name) and the
        value is the error message to raise (with a ValidationError).
        :return: dict
        """
        return {}

    @api.multi
    def _display_error_message(self, exception):
        """
        Load error messages depending on index name and raise the
        ValidationError with the correct message
        :param exception: Exception object
        :return:
        """
        try:
            # If we have an AttributeError to read the constraint name, it
            # could come from the exception who doesn't have the expected
            # format. In this case, we have to re-raise the
            # original expression but with a ValidationError
            constraint_name = exception.diag.constraint_name
        except AttributeError:
            raise exceptions.ValidationError(str(exception))
        message = self._get_exception_messages().get(
            constraint_name, str(exception))
        raise exceptions.ValidationError(message)

    @api.model
    def create(self, vals):
        """

        :param vals: dict
        :return: self recordset
        """
        res = False
        try:
            res = super().create(vals)
        except IntegrityError as e:
            self._display_error_message(e)

        if res and self._context.get('migration') and vals.get('create_date'):
            if vals.get('write_date'):
                q = 'update %s set create_date=%s, write_date=%s where id=%s'
                p = (AsIs(self._table), vals['create_date'],
                     vals['write_date'], res.id)
            else:
                q = 'update %s set create_date=%%s where id=%%s'
                p = (AsIs(self._table), vals['create_date'], res.id)
            self.env.cr.execute(q, p)
        return res

    @api.multi
    def write(self, vals):
        """
        If the current recordset is deactivate (active = False), deactivate
        also children (given by _get_active_relations() function on ir.model)
        :param vals: dict
        :return: bool
        """
        if 'active' in vals:
            mode = 'activate' if vals.get('active') else 'deactivate'
            expire_date = vals.get('expire_date')
            vals.update(self._get_fields_to_update(mode))
            if mode == 'deactivate':
                if expire_date:
                    vals.update({
                        'expire_date': expire_date,
                    })
                if self._inactive_cascade:
                    self._invalidate_active_relations()
        try:
            return super().write(vals)
        except IntegrityError as e:
            self._display_error_message(e)

    @api.multi
    def action_invalidate(self, vals=None):
        """
        Invalidates a recordset
        :param vals: dict
        :return: bool
        """
        vals = vals or {}
        vals.update(self._get_fields_to_update('deactivate'))
        return self.write(vals)

    @api.multi
    def action_revalidate(self, vals=None):
        """
        Reactivates a recordset
        :param vals: dict
        :return: bool
        """
        vals = vals or {}
        vals.update(self._get_fields_to_update('activate'))
        return self.write(vals)

    @api.model
    def _get_fields_to_update(self, mode):
        """
        Depending on a mode, builds a dictionary allowing to update validity
        fields
        :param mode: str
        :return: dict
        """
        result = {}
        if mode == 'deactivate':
            result.update({
                'active': False,
                'expire_date': fields.Datetime.now(),
            })
        if mode == 'activate':
            result.update({
                'active': True,
                'expire_date': False,
            })
        return result

    @api.multi
    @api.constrains('expire_date')
    def _check_invalidate(self):
        """
        Check if record can be deactivated, dependencies must be deactivated
        before
        :return:
        """
        self = self.sudo()
        invalidates = self
        invalidates -= self.filtered(lambda x: not x.expire_date)
        if invalidates:
            rels_dict = self.env['ir.model']._get_active_relations(invalidates)
            if rels_dict:
                for k, v in rels_dict.items():
                    _logger.info(
                        'Remaining active m2o for %s(%s): %s',
                        self._name, k, v)
                raise ValidationError(_('Invalidation not allowed: at least '
                                        'one dependency is still active'))

    @api.multi
    def _invalidate_active_relations(self):
        """
        Invalidate all dependencies of object ids
        """
        if self:
            ignore_relations = ['mail.followers', 'mail.notification']
            rels_dict = self.env['ir.model']._get_active_relations(
                self, with_ids=True)
            for relation_models in rels_dict.values():
                for relation, relation_ids in relation_models.items():
                    relation_object = self.env.get(relation)
                    if hasattr(relation_object, 'action_invalidate'):
                        relation_ids.action_invalidate()
                    elif relation in ignore_relations:
                        # Unlink obsolete followers. Sudo rights are required.
                        relation_ids.sudo().unlink()
                    elif hasattr(relation_object, 'active'):
                        relation_ids.write({'active': False})
