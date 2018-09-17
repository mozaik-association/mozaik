# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    int_instance_ids = fields.One2many(
        comodel_name='int.instance',
        inverse_name='product_pricelist_id',
        string='Instances',
        help="Internal instances using this price list",
        readonly=True,
    )

    @api.multi
    @api.constrains('int_instance_ids')
    def _check_number_int_instance(self):
        """
        Odoo constrain to ensure a price list is only used into 1 instance.
        :return:
        """
        bad_pricelists = self.filtered(lambda p: len(p.int_instance_ids) > 1)
        if bad_pricelists:
            details = "\n- ".join(bad_pricelists.mapped("display_name"))
            message = _("These price lists are already linked to Internal "
                        "Instances. Please choose another one or create a "
                        "new price list for your instances.\n -%s") % details
            raise exceptions.ValidationError(message)
