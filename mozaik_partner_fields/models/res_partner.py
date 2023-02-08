# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

inverse_operators = str.maketrans("<>", "><")


def compute_age(birth_date):
    """
    Compute age depending on a birth_date and today
    :param birth_date: string
    :return: int
    """
    if not birth_date:
        return False
    born = datetime.strptime(
        birth_date.strftime(DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT
    )
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class ResPartner(models.Model):

    _inherit = "res.partner"

    marital = fields.Selection(
        [
            ("single", "Single"),
            ("married", "Married"),
            ("cohabitant", "Legal Cohabitant"),
            ("widower", "Widower"),
            ("divorced", "Divorced"),
            ("separated", "Separated"),
            ("unmarried", "Unmarried"),
        ],
        tracking=True,
    )
    secondary_email = fields.Char()
    secondary_website = fields.Char(
        tracking=True,
    )
    social_twitter = fields.Char(
        "Twitter Account",
        tracking=True,
    )
    social_facebook = fields.Char(
        "Facebook Account",
        tracking=True,
    )
    social_youtube = fields.Char(
        "Youtube Account",
        tracking=True,
    )
    social_linkedin = fields.Char(
        "LinkedIn Account",
        tracking=True,
    )
    social_instagram = fields.Char(
        "Instagram Account",
        tracking=True,
    )
    age = fields.Integer(
        compute="_compute_age",
        search="_search_age",
    )

    # complete existing fields
    website = fields.Char(
        tracking=True,
    )
    comment = fields.Text(
        tracking=True,
    )
    birthdate_date = fields.Date(
        index=True,
        tracking=True,
    )
    nationality_id = fields.Many2one(
        tracking=True,
    )
    gender = fields.Selection(
        tracking=True,
    )
    introduction = fields.Text()

    is_user = fields.Boolean(compute="_compute_is_user", store=True)

    @api.depends("user_ids")
    def _compute_is_user(self):
        for record in self.with_context(active_test=False):
            record.is_user = len(record.user_ids.ids)

    @api.depends("birthdate_date")
    def _compute_age(self):
        """
        Compute age of partner depending of the birth date
        """
        for partner in self:
            partner.age = compute_age(partner.birthdate_date)

    @api.model
    def _search_age(self, operator, value):
        """
        Use birthdate_date to search on age
        """
        age = value
        birth_date = date.today() - relativedelta(years=age)
        birth_date = datetime.strftime(birth_date, DEFAULT_SERVER_DATE_FORMAT)
        op = operator.translate(inverse_operators)
        return [("birthdate_date", op, birth_date)]
