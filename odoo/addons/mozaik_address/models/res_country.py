# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm


class res_country(orm.Model):

    _inherit = "res.country"

    def _country_default_get(self, cr, uid, country_code, context=None):
        country_id = self.search(
            cr, uid, [('code', '=', country_code)], context=context)
        if country_id:
            return country_id[0]
        return False

    def _get_linked_addresses(self, cr, uid, ids, context=None):
        return self.pool.get('address.address').search(
            cr, uid, [('country_id', 'in', ids)], context=context)

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        Return all partners ids linked to country ids
        :param: ids
        :type: list of country ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        adr_ids = self._get_linked_addresses(cr, uid, ids, context=context)
        return self.pool['address.address'].get_linked_partners(
            cr, uid, adr_ids, context=context)
