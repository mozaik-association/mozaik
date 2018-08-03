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

from openerp.addons.document.content_index import indexer, cntIndex
from openerp.addons.document.std_index import ImageNoIndex
from .document import WIN


class CsvNoIndex(indexer):
    def _getMimeTypes(self):
        return ['text/csv']

    def _getExtensions(self):
        return ['.csv']

    def _doIndexContent(self, content):
        return 'csv'


cntIndex.register(CsvNoIndex())


class VcardNoIndex(indexer):
    def _getMimeTypes(self):
        return ['text/vcard']

    def _getExtensions(self):
        return ['.vcf']

    def _doIndexContent(self, content):
        return 'vcard'


cntIndex.register(VcardNoIndex())


class ImgNoIndex(ImageNoIndex):

    def _getExtensions(self):
        '''
        Under windows avoid to execute the Linux command 'file -b --mime'
        to determine the mimetype when trying to index ... an image
        '''
        if WIN:
            return ['.png', '.jpg', '.gif', '.jpeg', '.bmp', '.tiff', ]
        return super(ImgNoIndex, self)._getExtensions()


cntIndex.register(ImgNoIndex())
