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
