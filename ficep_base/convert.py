# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp.tools.convert import xml_import

_logger = logging.getLogger(__name__)


# Replace the xml_import._tag_delete functions

original_xml_import_tag_delete = xml_import._tag_delete


def xml_import_tag_delete(self, cr, rec, data_node=None):
    '''
    Do not raise exception if requesting to delete a record already deleted
    '''
    fct_src = original_xml_import_tag_delete
    try:
        fct_src(self, cr, rec, data_node=data_node)
    except:
        _logger.warning('xml id "%s" is already deleted' % rec.get('id', ''))

xml_import._tag_delete = xml_import_tag_delete

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
