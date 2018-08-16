# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


class CommonCoordinate(object):
    """
    Common class who instantiate some models used for current tests
    """

    def setUp(self):
        super(CommonCoordinate, self).setUp()
        # Must be updated by concrete tests/implementation
        self.model_coordinate_wizard = None
        self.model_coordinate = None
        self.coo_into_partner = None
