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

import tempfile
import vobject
import codecs

from openerp.tools.translate import _
from openerp.osv import orm, fields


class export_vcard(orm.TransientModel):
    _name = 'export.vcard'
    _description = 'Export vCard Wizard'

    _columns = {
    }

    def export(self, cr, uid, ids, context=None):
        vcard_content = self.get_vcard(cr, uid, context and context.get('active_ids', False) or False, context=context)

        # Send to current user
        attachment = [('Extract.vcf', vcard_content)]
        partner_ids = self.pool['res.partner'].search(cr, uid, [('user_ids', '=', uid)], context=context)
        if partner_ids:
            self.pool['mail.thread'].message_post(cr, uid, False, attachments=attachment, context=context,
                                                  partner_ids=partner_ids, subject=_('Export VCF'))
        return True

    def get_vcard(self, cr, uid, email_coordinate_ids, context=None):
        """
        ============
        get_vcard
        ============
        Create a VCF file with the specified coordinates.
        :type email_coordinate_ids: []
        """
        if not email_coordinate_ids:
            return False

        tmp = tempfile.NamedTemporaryFile(prefix='vCard', suffix=".vcf", delete=False)
        f = codecs.open(tmp.name, "r+", "utf-8")

        def safe_get(o, attr, default=None):
            try:
                return getattr(o, attr)
            except orm.except_orm:
                return default

        def _get_unicode(data):
            return data and unicode(data) or False

        for ec in self.pool['email.coordinate'].browse(cr, uid, email_coordinate_ids):
            partner = safe_get(ec, 'partner_id')
            if not partner:
                continue

            card = vobject.vCard()
            card.add('fn').value = _get_unicode(partner.printable_name)
            if not partner.usual_lastname and not partner.firstname:
                card.add('n').value = vobject.vcard.Name(_get_unicode(partner.printable_name))
            else:
                card.add('n').value = vobject.vcard.Name(
                    _get_unicode(partner.usual_lastname) or _get_unicode(partner.lastname) or '',
                    _get_unicode(partner.firstname))

            emailpart = card.add('email')
            emailpart.value = _get_unicode(ec.email)
            emailpart.type_param = 'INTERNET'

            if partner.fix_coordinate_id and partner.fix_coordinate_id.phone_id:
                fix_part = card.add('tel')
                fix_part.type_param = 'WORK'
                fix_part.value = partner.fix_coordinate_id.phone_id.name

            if partner.mobile_coordinate_id and partner.mobile_coordinate_id.phone_id:
                fix_part = card.add('tel')
                fix_part.type_param = 'CELL'
                fix_part.value = partner.mobile_coordinate_id.phone_id.name

            # CHEKME: add more informations? http://www.evenx.com/vcard-3-0-format-specification
            # TODO: verify and fix utf-8 encoding

            f.write(card.serialize().decode('utf-8'))

        f.close()
        f = open(tmp.name, "r")
        vcard_content = f.read()
        f.close()
        return vcard_content

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
