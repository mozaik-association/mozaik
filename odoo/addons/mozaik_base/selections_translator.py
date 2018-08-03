# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from operator import itemgetter


def dict_map(f, d):
    return dict((k, f(v)) for k, v in d.items())


def _find_fieldname(model, field):
    inherit_columns = dict_map(itemgetter(2), model._inherit_fields)
    all_columns = dict(inherit_columns, **model._columns)
    for fn in all_columns:
        if all_columns[fn] is field:
            return fn
    raise ValueError('Field not found: %r' % (field,))


class selection_converter(object):
    """Format the selection in the browse record objects"""
    def __init__(self, value):
        self._value = value
        self._str = value

    def set_value(self, cr, uid, _self_again, record, field, lang):
        # this design is terrible
        # search fieldname from the field
        fieldname = _find_fieldname(record._table, field)
        context = dict(lang=lang.code)
        fg = record._table.fields_get(cr, uid, [fieldname], context=context)
        selection = dict(fg[fieldname]['selection'])
        self._str = selection[self.value]

    @property
    def value(self):
        return self._value

    def __str__(self):
        return self._str

# Use following dictionary as value for fields_process attribute of browse
# method
#    It will return the translated value for selections fields
#    Example :
#    record = self.browse(cr, uid, obj_id, context=context,
# fields_process=translate_selections)

translate_selections = {'selection': selection_converter}
