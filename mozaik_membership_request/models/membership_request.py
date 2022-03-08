# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from collections import OrderedDict
from datetime import date, datetime
from operator import attrgetter
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import safe_eval
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.mozaik_tools.tools import (
    check_and_format_number,
    check_email,
    format_email,
    get_age,
)

_logger = logging.getLogger(__name__)

MEMBERSHIP_AVAILABLE_STATES = [
    ("draft", "Draft"),
    ("confirm", "Confirmed"),
    ("validate", "Done"),
    ("cancel", "Cancelled"),
]

EMPTY_ADDRESS = "0#0#0#0#0#0#0#0"
MEMBERSHIP_REQUEST_TYPE = [
    ("m", "Member"),
    ("s", "Supporter"),
]
MR_REQUIRED_AGE_KEY = "mr_required_age"


def partner_add_values(mr, partner_values):
    if not mr.is_company:
        partner_values["firstname"] = mr.firstname
        if mr.gender:
            partner_values["gender"] = mr.gender
        if mr.birthdate_date:
            partner_values["birthdate_date"] = mr.birthdate_date

    if mr.nationality_id:
        partner_values["nationality_id"] = mr.nationality_id.id


class MembershipRequest(models.Model):

    _name = "membership.request"
    _inherit = ["mozaik.abstract.model"]
    _description = "Membership Request"
    _inactive_cascade = True
    _terms = ["interest_ids", "competency_ids"]
    _order = "id desc"
    _unicity_keys = "N/A"

    identifier = fields.Char(related="partner_id.identifier", string="Identifier")
    is_company = fields.Boolean("Is a Company", default=False)
    lastname = fields.Char("Name", required=True, tracking=True)
    firstname = fields.Char("Firstname", tracking=True)

    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        string="Gender",
        index=True,
        tracking=True,
    )
    email = fields.Char("Email", tracking=True)
    phone = fields.Char("Phone", tracking=True)
    mobile = fields.Char("Mobile", tracking=True)
    day = fields.Char("Day")
    month = fields.Char("Month")
    year = fields.Char("Year")
    birthdate_date = fields.Date("Birth Date", tracking=True)

    # request and states
    request_type = fields.Selection(
        selection=MEMBERSHIP_REQUEST_TYPE, string="Request Type", tracking=True
    )
    membership_state_id = fields.Many2one(
        comodel_name="membership.state", string="Current State"
    )
    result_type_id = fields.Many2one(
        comodel_name="membership.state", string="Expected State"
    )
    is_update = fields.Boolean(string="Is Update", default=False)
    state = fields.Selection(
        selection=MEMBERSHIP_AVAILABLE_STATES,
        string="State",
        tracking=True,
        default="draft",
    )

    # address
    country_id = fields.Many2one(
        comodel_name="res.country", string="Country", index=True, tracking=True
    )
    enforce_cities = fields.Boolean(related="country_id.enforce_cities", readonly=True)

    city_id = fields.Many2one(comodel_name="res.city", string="City", tracking=True)
    local_zip = fields.Char(related="city_id.zipcode", string="Local Zip", store=True)
    zip_man = fields.Char(string="Zip", tracking=True)

    city_man = fields.Char(string="City (Manual)", tracking=True)

    address_local_street_id = fields.Many2one(
        comodel_name="address.local.street",
        string="Reference Street",
        tracking=True,
    )
    street_man = fields.Char(string="Street", tracking=True)
    street2 = fields.Char(string="Street2", tracking=True)

    number = fields.Char(string="Number", tracking=True)
    box = fields.Char(string="Box", tracking=True)
    sequence = fields.Integer(string="Sequence", tracking=True, group_operator="min")

    technical_name = fields.Char(string="Technical Name")

    # indexes
    interest_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        relation="membership_request_interests_rel",
        column1="membership_id",
        column2="thesaurus_term_id",
        string="Interests",
    )
    competency_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        relation="membership_request_competence_rel",
        column1="membership_id",
        column2="thesaurus_term_id",
        string="Competencies",
    )

    note = fields.Text("Notes")

    # references
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        domain="[('membership_state_id', '!=', False)]",
    )

    int_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="Internal Instance (real)",
    )
    int_instance_ids_readonly = fields.Many2many(
        related="int_instance_ids",
        string="Internal Instance",
    )
    force_int_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Internal Instance (to Force)",
        tracking=True,
    )

    address_id = fields.Many2one(
        comodel_name="address.address", string="Address", tracking=True
    )
    change_ids = fields.One2many(
        comodel_name="membership.request.change",
        inverse_name="membership_request_id",
        string="Changes",
        domain=[("active", "=", True)],
    )
    inactive_change_ids = fields.One2many(
        comodel_name="membership.request.change",
        inverse_name="membership_request_id",
        string="Changes (Inactive)",
        domain=[("active", "=", False)],
    )

    age = fields.Integer(string="Age", compute="_compute_age", search="_search_age")

    local_voluntary = fields.Boolean(tracking=True)
    regional_voluntary = fields.Boolean(tracking=True)
    national_voluntary = fields.Boolean(tracking=True)
    local_only = fields.Boolean(
        tracking=True, help="Partner wishing to be contacted only by the local"
    )

    involvement_category_ids = fields.Many2many(
        "partner.involvement.category",
        relation="membership_request_involvement_category_rel",
        column1="request_id",
        column2="category_id",
        string="Involvement Categories",
    )

    indexation_comments = fields.Text("Indexation comments")

    amount = fields.Float(digits="Product Price", copy=False)
    reference = fields.Char(copy=False)
    effective_time = fields.Datetime(copy=False, string="Involvement Date")

    nationality_id = fields.Many2one(
        comodel_name="res.country", string="Nationality", tracking=True
    )

    @api.model
    def _get_status_values(self, request_type, date_from=False):
        """
        :type request_type: char
        :param request_type: m or s for member or supporter.
            `False` if not defined
        :rtype: dict
        :rparam: affected date resulting of the `request_type`
            and the `status`
        """
        vals = {}
        if request_type in ["m", "s"]:
            vals["accepted_date"] = date_from or fields.Date.today()
            vals["free_member"] = request_type == "s"
        return vals

    @api.constrains("birthdate_date", "is_company", "state")
    def _check_age(self):
        required_age = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(MR_REQUIRED_AGE_KEY, default=16)
        )
        for mr in self.filtered(
            lambda s: not s.is_company
            and s.birthdate_date
            and s.request_type
            and s.state == "validate"
        ):
            if mr.age < required_age:
                raise ValidationError(
                    _("The required age for a membership request is %s") % required_age
                )

    def _search_age(self, operator, value):
        """
        Use birthdate_date to search on age
        """
        age = value
        computed_birthdate_date = date.today() - relativedelta(years=age)
        computed_birthdate_date = datetime.strftime(
            computed_birthdate_date, DEFAULT_SERVER_DATE_FORMAT
        )
        if operator == ">=":
            operator = "<="
        elif operator == "<":
            operator = ">"
        return [("birthdate_date", operator, computed_birthdate_date)]

    def _pop_related(self, vals):
        vals.pop("local_zip", None)
        vals.pop("identifier", None)

    @api.depends("is_company", "birthdate_date")
    def _compute_age(self):
        """
        age computed depending of the birth date of the
        membership request
        """
        for mr in self:
            if not mr.is_company and mr.birthdate_date:
                mr.age = get_age(mr.birthdate_date)
            else:
                mr.age = 0

    def _get_membership_tracked_fields(self):
        """
        This method return a list of tuple defining which fields
        must create a change record.
        Tuple is structured like:
         - sequence: n° of sequence of the change, it respect the display
                     order on the screen view
         - field name: field name on view
         - request path: path to the field value from the request object
         - partner_path: path to the field value from the partner object
         - label: label to be able to ignore comparison
        """
        partner_address_path = "address_address_id"
        return [
            (1, "lastname", "lastname", "lastname", ""),
            (2, "firstname", "firstname", "firstname", ""),
            (3, "birthdate_date", "birthdate_date", "birthdate_date", ""),
            (4, "phone", "phone", "phone", ""),
            (5, "gender", "gender", "gender", ""),
            (6, "mobile", "mobile", "mobile", ""),
            (7, "email", "email", "email", ""),
            (
                8,
                "country_id",
                "country_id.display_name",
                partner_address_path + ".country_id.display_name",
                "",
            ),
            # address_local_zip_id set on request AND on partner
            (
                9,
                "city_id",
                "city_id.display_name",
                partner_address_path + ".city_id.display_name",
                "ZIP_REQUEST_PARTNER",
            ),
            # city_id set on request AND not on partner
            (
                9,
                "city_id",
                "city_id.zipcode",
                partner_address_path + ".zip_man",
                "ZIP_REQUEST_NO_PARTNER",
            ),
            (
                9,
                "city_id",
                "city_id.name",
                partner_address_path + ".city_man",
                "ZIP_REQUEST_NO_PARTNER",
            ),
            # city_id not set on request but on partner
            (
                9,
                "zip_man",
                "zip_man",
                partner_address_path + "city_id.zipcode",
                "ZIP_NO_REQUEST_PARTNER",
            ),
            (
                9,
                "city_man",
                "city_man",
                partner_address_path + ".city_id.name",
                "ZIP_NO_REQUEST_PARTNER",
            ),
            # city_id not set on request and not on partner
            (
                9,
                "zip_man",
                "zip_man",
                partner_address_path + ".zip_man",
                "ZIP_NO_REQUEST_NO_PARTNER",
            ),
            (
                9,
                "city_man",
                "city_man",
                partner_address_path + ".city_man",
                "ZIP_NO_REQUEST_NO_PARTNER",
            ),
            # address_local_street_id set on request AND on partner
            (
                10,
                "address_local_street_id",
                "address_local_street_id.display_name",
                partner_address_path + ".address_local_street_id.display_name",
                "STREET_REQUEST_PARTNER",
            ),
            # address_local_street_id set on request AND not on partner
            (
                10,
                "address_local_street_id",
                "address_local_street_id.display_name",
                partner_address_path + ".street_man",
                "ZIP_REQUEST_NO_PARTNER",
            ),
            # address_local_street_id not set on request but on partner
            (
                10,
                "street_man",
                "street_man",
                partner_address_path + ".address_local_street_id.display_name",
                "STREET_NO_REQUEST_PARTNER",
            ),
            # address_local_street_id not set on request and not partner
            (
                10,
                "street_man",
                "street_man",
                partner_address_path + ".street_man",
                "STREET_NO_REQUEST_NO_PARTNER",
            ),
            (11, "number", "number", partner_address_path + ".number", "NUMBER"),
            (12, "street2", "street2", partner_address_path + ".street2", "STREET2"),
            (13, "box", "box", partner_address_path + ".box", "BOX"),
            (
                14,
                "sequence",
                "sequence",
                partner_address_path + ".sequence",
                "SEQUENCE",
            ),
            (
                15,
                "int_instance_ids",
                "expr: request.force_int_instance_id.name or "
                "request.int_instance_ids.name",
                "int_instance_ids.name",  # TODO?
                "",
            ),
            (16, "local_voluntary", "local_voluntary", "local_voluntary", "LOCAL"),
            (
                17,
                "regional_voluntary",
                "regional_voluntary",
                "regional_voluntary",
                "REGIONAL",
            ),
            (
                18,
                "national_voluntary",
                "national_voluntary",
                "national_voluntary",
                "NATIONAL",
            ),
            (19, "local_only", "local_only", "local_only", "LOCAL-ONLY"),
            (20, "nationality_id", "nationality_id.name", "nationality_id.name", ""),
        ]

    def _clean_stored_changes(self):
        chg_obj = self.env["membership.request.change"]
        chg_ids = chg_obj.search([("membership_request_id", "in", self.ids)])
        if chg_ids:
            return chg_ids.unlink()

        return False

    def _get_labels_to_process(self, request):
        label_path = [
            "LOCAL",
            "REGIONAL",
            "NATIONAL",
            "LOCAL-ONLY",
        ]
        if not request.country_id:
            return label_path
        label_path = [
            "NUMBER",
            "STREET2",
            "BOX",
            "SEQUENCE",
        ] + label_path
        partner_adr = request.partner_id.address_address_id
        if request.city_id and partner_adr.city_id:
            label_path.append("ZIP_REQUEST_PARTNER")
        elif request.city_id and not partner_adr.city_id:
            label_path.append("ZIP_REQUEST_NO_PARTNER")
        elif not request.city_id and partner_adr.city_id:
            label_path.append("ZIP_NO_REQUEST_PARTNER")
        else:
            label_path.append("ZIP_NO_REQUEST_NO_PARTNER")

        if request.address_local_street_id and partner_adr.address_local_street_id:
            label_path.append("STREET_REQUEST_PARTNER")
        elif (
            request.address_local_street_id and not partner_adr.address_local_street_id
        ):
            label_path.append("STREET_REQUEST_NO_PARTNER")
        elif (
            not request.address_local_street_id and partner_adr.address_local_street_id
        ):
            label_path.append("STREET_NO_REQUEST_PARTNER")
        else:
            label_path.append("STREET_NO_REQUEST_NO_PARTNER")
        return label_path

    def _detect_changes(self):
        tracked_fields = self._get_membership_tracked_fields()
        fields_def = self.fields_get([elem[1] for elem in tracked_fields])
        res = {}
        chg_obj = self.env["membership.request.change"]
        self._clean_stored_changes()

        for request in self:
            if not request.partner_id:
                res[request.id] = False
                continue
            label_to_process = self._get_labels_to_process(request)

            for element in tracked_fields:
                seq, field, request_path, partner_path, label = element
                if label and label not in label_to_process:
                    continue
                if request_path.startswith("expr: "):
                    request_value = safe_eval.safe_eval(
                        request_path[6:], {"request": request}
                    )
                else:
                    request_value = attrgetter(request_path)(request)
                partner_value = attrgetter(partner_path)(request.partner_id)
                field = fields_def[field]

                if (request_value or label) and request_value != partner_value:
                    if "selection" in field:
                        selection = dict(field["selection"])
                        request_value = selection.get(request_value)
                        partner_value = selection.get(partner_value)
                    if isinstance(request_value, bool) and isinstance(
                        partner_value, bool
                    ):
                        request_value = request_value and _("Yes") or _("No")
                        partner_value = partner_value and _("Yes") or _("No")
                    vals = {
                        "membership_request_id": request.id,
                        "sequence": seq,
                        "field_name": field["string"],
                        "old_value": partner_value,
                        "new_value": request_value,
                    }
                    chg_obj.create(vals)

    @api.model
    def _pre_process(self, vals):
        """
        * Try:
        ** to find a zipcode and a country
        ** to build a birthdate_date
        ** to find an existing partner
        ** to find coordinates

        :rparam vals: updated input values dictionary ready
                      to create a ``membership_request``
        """
        is_company = vals.get("is_company", False)
        firstname = False if is_company else vals.get("firstname", False)
        lastname = vals.get("lastname", False)
        birthdate_date = False if is_company else vals.get("birthdate_date", False)
        day = False if is_company else vals.get("day", False)
        month = False if is_company else vals.get("month", False)
        year = False if is_company else vals.get("year", False)
        gender = False if is_company else vals.get("gender", False)
        email = vals.get("email", False)
        mobile = vals.get("mobile", False)
        phone = vals.get("phone", False)
        address_id = vals.get("address_id", False)
        address_local_street_id = vals.get("address_local_street_id", False)
        city_id = vals.get("city_id", False)
        number = vals.get("number", False)
        box = vals.get("box", False)
        city_man = vals.get("city_man", False)
        country_id = vals.get("country_id", False)
        zip_man = vals.get("zip_man", False)
        street_man = vals.get("street_man", False)

        partner_id = vals.get("partner_id", False)

        request_type = vals.get("request_type", False)

        zids = False
        if zip_man and city_man:
            domain = [
                ("zipcode", "=", zip_man),
                ("name", "ilike", city_man),
            ]
            zids = self.env["res.city"].search(domain, limit=1)
        if not zids and zip_man and not city_man and not country_id:
            domain = [
                ("zipcode", "=", zip_man),
            ]
            zids = self.env["res.city"].search(domain, limit=1)
        if zids:
            cnty_id = self.env["res.country"]._country_default_get("BE").id
            if not country_id or cnty_id == country_id:
                country_id = cnty_id
                city_id = zids.id
                city_man = False
                zip_man = False

        if not is_company and not birthdate_date:
            birthdate_date = self.get_birthdate_date(day, month, year)
        if mobile:
            mobile = self.get_format_phone_number(mobile)
        if phone:
            phone = self.get_format_phone_number(phone)
        if email:
            email = self.get_format_email(email)

        if not partner_id:
            partner = self.get_partner_id(
                is_company, birthdate_date, lastname, firstname, email
            )
            if partner:
                partner_id = partner.id

        technical_name = self.get_technical_name(
            address_local_street_id,
            city_id,
            number,
            box,
            city_man,
            street_man,
            zip_man,
            country_id,
        )
        address_id = (
            address_id
            or self.env["address.address"]
            .sudo()
            .search([("technical_name", "=", technical_name)], limit=1)
            .id
        )
        int_instance_id = self.get_int_instance_id(city_id)

        res = self._onchange_partner_id_vals(
            is_company, request_type, partner_id, technical_name
        )
        vals.update(res)

        vals.update(
            {
                "is_company": is_company,
                "partner_id": partner_id,
                "lastname": lastname,
                "firstname": firstname,
                "birthdate_date": birthdate_date,
                "int_instance_ids": res.get("int_instance_ids")
                or [(6, 0, [int_instance_id])],
                "day": day,
                "month": month,
                "year": year,
                "gender": gender,
                "mobile": mobile,
                "phone": phone,
                "email": email,
                "address_id": address_id,
                "city_id": city_id,
                "country_id": country_id,
                "zip_man": zip_man,
                "city_man": city_man,
                "technical_name": technical_name,
            }
        )

        return vals

    @api.onchange("country_id")
    def onchange_country_id(self):
        self_sudo = self.sudo()
        for req in self_sudo:
            vals = {
                "city_id": False,
                "technical_name": self_sudo.get_technical_name(
                    False,
                    False,
                    self.number,
                    self.box,
                    self.city_man,
                    self.street_man,
                    self.zip_man,
                    self.country_id.id,
                ),
                "int_instance_ids": [(6, 0, [self.get_int_instance_id(False)])],
            }
            req.update(vals)

    @api.onchange("city_id")
    def onchange_city_id(self):
        self_sudo = self.sudo()
        for req in self_sudo:
            vals = {
                "address_local_street_id": False,
                "technical_name": self_sudo.get_technical_name(
                    False,
                    self_sudo.city_id.id,
                    self_sudo.number,
                    self_sudo.box,
                    self_sudo.city_man,
                    self_sudo.street_man,
                    self_sudo.zip_man,
                    self_sudo.country_id.id,
                ),
                "local_zip": self_sudo.city_id.zipcode,
                "int_instance_ids": [
                    (6, 0, [self.get_int_instance_id(self_sudo.city_id.id)])
                ],
            }
            req.update(vals)

    # view methods: onchange, button

    @api.onchange(
        "zip_man", "city_man", "address_local_street_id", "street_man", "number", "box"
    )
    def onchange_other_address_componants(self):
        for req in self.sudo():
            req.technical_name = req.get_technical_name(
                req.address_local_street_id.id,
                req.city_id.id,
                req.number,
                req.box,
                req.city_man,
                req.street_man,
                req.zip_man,
                req.country_id.id,
            )

    @api.onchange("technical_name")
    def onchange_technical_name(self):
        for req in self.sudo():
            address_ids = (
                self.env["address.address"]
                .sudo()
                .search([("technical_name", "=", req.technical_name)], limit=1)
            )
            req.address_id = address_ids

    @api.onchange("lastname", "firstname", "day", "month", "year", "email")
    def onchange_partner_component(self):
        """
        try to find a new partner_id depending of the
        birthdate_date, lastname, firstname, email
        """
        for req in self.sudo():
            birthdate_date = False
            if not req.is_company:
                birthdate_date = self.get_birthdate_date(req.day, req.month, req.year)
            email = self.get_format_email(req.email)

            req.birthdate_date = "%s" % birthdate_date if birthdate_date else False
            req.email = email
            if req.is_update:
                continue

            partner_id = self.get_partner_id(
                req.is_company, birthdate_date, req.lastname, req.firstname, email
            )

            req.partner_id = partner_id

    @api.onchange("partner_id", "request_type", "is_company")
    def onchange_partner_id(self):
        """
        Take current
            * membership_state_id
            * interest_ids
            * competency_ids
            * voluntaries
        of ``partner_id``
        And set corresponding fields into the ``membership.request``

        **Note**
        fields are similarly named
        """
        self.env["membership.request"].sudo()
        for req in self:
            req.update(
                req._onchange_partner_id_vals(
                    req.is_company,
                    req.request_type,
                    req.partner_id.id,
                    req.technical_name,
                )
            )

    @api.model
    def _onchange_partner_id_vals(
        self, is_company, request_type, partner_id, technical_name
    ):
        """
        Take current
            * membership_state_id
            * interest_ids
            * competency_ids
            * voluntaries
        of ``partner_id``
        And set corresponding fields into the ``membership.request``

        **Note**
        fields are similarly named
        """
        res = {
            "interest_ids": False,
            "competency_ids": False,
            "identifier": False,
        }
        def_status_id = self.env["membership.state"]._get_default_state()
        partner_status_id = False
        membership_state_code = False
        if partner_id:
            partner = self.env["res.partner"].sudo().browse(partner_id)
            # take current status of partner
            partner_status_id = (
                partner.membership_state_id and partner.membership_state_id.id or False
            )
            membership_state_code = partner.membership_state_code
            interests_ids = [term.id for term in partner.interest_ids]
            res["interest_ids"] = interests_ids and [[6, False, interests_ids]] or False
            competency_ids = [trm.id for trm in partner.competency_ids]
            res["competency_ids"] = (
                competency_ids and [[6, False, competency_ids]] or False
            )
            res["identifier"] = partner.identifier

            if technical_name == EMPTY_ADDRESS:
                res["int_instance_ids"] = partner.int_instance_ids.ids

            res["local_voluntary"] = partner.local_voluntary
            res["regional_voluntary"] = partner.regional_voluntary
            res["national_voluntary"] = partner.national_voluntary
            res["local_only"] = partner.local_only

        elif not is_company:
            partner_status_id = def_status_id.id

        result_type = self.env["membership.state"]
        if not is_company:
            result_type = self.get_partner_preview(request_type, partner_id)
        else:
            res.update(
                {
                    "request_type": False,
                }
            )
        if result_type.code in [
            False,
            "without_membership",
            "supporter",
            "former_supporter",
        ]:
            res.update(
                {
                    "local_voluntary": False,
                    "regional_voluntary": False,
                    "national_voluntary": False,
                }
            )
        elif any(
            [
                result_type.code == "member_candidate"
                and membership_state_code in [False, "without_membership", "supporter"],
                result_type.code == "member_committee"
                and membership_state_code == "supporter",
            ]
        ):
            res.update(
                {
                    "local_voluntary": True,
                    "regional_voluntary": True,
                    "national_voluntary": True,
                }
            )
        if result_type.code in [
            "supporter",
            "former_supporter",
            "member_candidate",
            "member_committee",
            "member",
            "former_member",
            "former_member_committee",
        ]:
            res["local_only"] = False

        res.update(
            {
                "membership_state_id": partner_status_id,
                "result_type_id": result_type.id if result_type else False,
            }
        )
        return res

    @api.onchange("mobile")
    def onchange_mobile(self):
        for req in self:
            req.mobile = self.get_format_phone_number(req.mobile)

    @api.onchange("phone")
    def onchange_phone(self):
        for req in self:
            req.phone = self.get_format_phone_number(req.phone)

    # public method
    @api.model
    def get_partner_preview(self, request_type, partner_id=False):
        """
        Advance partner's workflow to catch the next state
        If no partner then create one
        See also write and create method in abstract_model, it is important
        that disable_tracking remains always True during the entire simulation
        :type request_type: char
        :param request_type: m or s (member or supporter)
        :type partner_id: res.partner
        :param partner_id: partner
        :rparam: next status in partner's workflow depending on `request_type`
        """
        self_context = self.with_context(tracking_disable=True)

        partner_obj = self_context.env["res.partner"]
        status_obj = self.env["membership.state"]
        former_member = self.env.ref("mozaik_membership.former_member")
        name = '"preview-%s"' % uuid4().hex
        self.flush()
        self.env.cr.execute("SAVEPOINT %(savepoint)s", {"savepoint": AsIs(name)})
        try:
            if partner_id:
                partner = partner_obj.browse(partner_id)
            else:
                partner_datas = {
                    "lastname": "%s" % uuid4(),
                    "identifier": "-1",
                }
                partner = partner_obj.create(partner_datas)
            # didn't find a good way to make it in the statechart
            event = None
            if partner.membership_state_id == former_member:
                event = "paid"
            vals = self._get_status_values(request_type)
            if vals:
                partner.write(vals)
            state_code = partner.simulate_next_state(event)
            partner.invalidate_cache(ids=partner.ids)
        finally:
            self.env.cr.execute(
                "ROLLBACK TO SAVEPOINT %(savepoint)s", {"savepoint": AsIs(name)}
            )
        return status_obj.search([("code", "=", state_code)], limit=1)

    def get_birthdate_date(self, day, month, year):
        """
        ==============
        get_birthdate_date
        ==============
        Return a birth date case where all parameters day/month/year
        are initialized
        """
        birthdate_date = False
        if day and month and year:
            try:
                birthdate_date = date(int(year), int(month), int(day)).strftime(
                    "%Y-%m-%d"
                )
            except Exception:
                _logger.info("Reset `birthdate_date`: Invalid Date")
        return birthdate_date

    def get_partner_id(self, is_company, birthdate_date, lastname, firstname, email):
        """
        Make special combinations of domains to try to find
        a unique partner_id
        """
        partner_obj = self.env["virtual.custom.partner"]
        partner_domains = []

        if not is_company and birthdate_date and email and firstname and lastname:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('birthdate_date','=', '%s'),"
                "('email', '=', '%s'),"
                "('firstname', 'ilike', \"%s\"),"
                "('lastname', 'ilike', \"%s\")]"
                % (birthdate_date, email, firstname, lastname)
            )
        if not is_company and birthdate_date and email:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('birthdate_date','=', '%s'),"
                "('email', '=', '%s')]" % (birthdate_date, email)
            )
        if not is_company and email and firstname and lastname:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('email', '=', '%s'),"
                "('firstname', 'ilike', \"%s\"),"
                "('lastname', 'ilike', \"%s\")]" % (email, firstname, lastname)
            )
        if not is_company and email:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('email', '=','%s')]" % (email)
            )
        if is_company and email:
            partner_domains.append(
                "[('is_company', '=', True)," "('email', '=','%s')]" % (email)
            )
        if lastname:
            if not is_company and firstname:
                partner_domains.append(
                    "[('membership_state_id','!=',False),"
                    "('is_company', '=', False),"
                    "('firstname', 'ilike', \"%s\"),"
                    "('lastname', 'ilike', \"%s\")]" % (firstname, lastname)
                )
            elif not is_company:
                partner_domains.append(
                    "[('membership_state_id', '!=', False),"
                    "('is_company', '=', False),"
                    '("lastname", \'ilike\', "%s")]' % (lastname)
                )
            else:
                partner_domains.append(
                    "[('is_company', '=', True),"
                    "('lastname', 'ilike', \"%s\")]" % (lastname)
                )

        partner_id = False
        virtual_partner_id = self.persist_search(partner_obj, partner_domains)
        # because this is not a real partner but a virtual partner
        if virtual_partner_id:
            partner_id = virtual_partner_id.partner_id
        return partner_id

    def persist_search(self, model_obj, domains):
        """
        This method will make a search with a list of domain and return result
        only if it is a single result
        :type model_obj: model object into odoo (ex: res.partner)
        :param model_obj: used to make the research
        :type domains: []
        :param domains: contains a list of domains
        :rparam: result of the search
        """

        def rec_search(loop_counter):
            if loop_counter >= len(domains):
                return False
            else:
                try:
                    domain = safe_eval.safe_eval(domains[loop_counter])
                except Exception as e:
                    raise ValidationError(_("Invalid Data")) from e
                model_ids = model_obj.search(domain)
                if len(model_ids) == 1:
                    return model_ids[0]
                else:
                    return rec_search(loop_counter + 1)

        return rec_search(0)

    def get_technical_name(
        self,
        address_local_street_id,
        city_id,
        number,
        box,
        city_man,
        street_man,
        zip_man,
        country_id,
    ):
        if not country_id:
            return EMPTY_ADDRESS
        local_zip = False
        if city_id:
            zip_man, city_man = False, False
            local_zip = self.env["res.city"].browse([city_id]).zipcode
        if address_local_street_id:
            street_man = False
        values = OrderedDict(
            [
                ("country_id", country_id),
                ("address_local_zip", local_zip),
                ("zip_man", zip_man),
                ("city_man", city_man),
                ("address_local_street_id", address_local_street_id),
                ("street_man", street_man),
                ("number", number),
                ("box", box),
            ]
        )
        address_obj = self.env["address.address"]
        technical_name = address_obj._get_technical_name(values)
        return technical_name

    def get_format_email(self, email):
        """
        ``Check and format`` email just like `email.coordinate` make it
        :rparam: formated email value
        """
        if email:
            if check_email(email):
                email = format_email(email)
        return email

    def get_format_phone_number(self, number):
        """
        Format a phone number with the same way as phone.phone do it.
        Call with a special context to avoid exception
        """
        if number:
            try:
                number = check_and_format_number(
                    number,
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("default.country.code", default="BE"),
                )
            except UserError:
                _logger.info("Unable to format phone number %s", number)

        return number

    def confirm_request(self):
        vals = {"state": "confirm"}
        # superuser_id because of record rules
        return self.sudo().write(vals)

    def validate_request(self):
        """
        First check if the relations are set. For those try to update
        content
        In Other cases then create missing required data
        """
        mr_vals = {}
        for mr in self:
            former_code = False
            if mr.partner_id:
                former_code = mr.partner_id.membership_state_code

            partner_values = {
                "is_company": mr.is_company,
                "lastname": mr.lastname,
            }
            partner_add_values(mr, partner_values)

            new_interests_ids = []
            if not mr.is_company:
                new_interests_ids = (
                    mr.interest_ids
                    and ([interest.id for interest in mr.interest_ids])
                    or []
                )
            new_competency_ids = (
                mr.competency_ids
                and ([competence.id for competence in mr.competency_ids])
                or []
            )

            notes = []
            if mr.note:
                notes.append(mr.note)
            if mr.partner_id and mr.partner_id.comment:
                notes.append(mr.partner_id.comment)

            indexation_comments = []
            if mr.indexation_comments:
                indexation_comments.append(mr.indexation_comments)
            if mr.partner_id and mr.partner_id.indexation_comments:
                indexation_comments.append(mr.partner_id.indexation_comments)

            partner_values.update(
                {
                    "competency_ids": [[6, False, new_competency_ids]],
                    "interest_ids": [[6, False, new_interests_ids]],
                    "comment": notes and "\n".join(notes) or False,
                    "indexation_comments": indexation_comments
                    and "\n".join(indexation_comments)
                    or False,
                }
            )

            # update_partner values
            # Passing do_not_track_twice in context the first tracking
            # evaluation through workflow will produce a notification
            # the second one out of workflow not (when context will be
            # pass through workflow this solution will not work anymore)
            mr = mr.with_context(do_not_track_twice=True)  # TODO does nothing for now?
            partner_obj = mr.env["res.partner"]  # we need to keep the modified context

            partner = mr.partner_id

            if not mr.partner_id:
                mr._get_instance_partner(partner_values)
                partner = partner_obj.create(partner_values)
                mr_vals["partner_id"] = partner.id
                partner_values = {}

            # create new involvements
            self._validate_request_involvement(mr, partner)

            new_code = mr.result_type_id.code
            # save voluntaries
            if new_code not in [
                False,
                "without_membership",
                "supporter",
                "former_supporter",
            ] and not any(
                [
                    new_code == "member_candidate"
                    and former_code in [False, "without_membership", "supporter"],
                    new_code == "member_committee" and former_code == "supporter",
                ]
            ):
                partner_values.update(
                    {
                        "local_voluntary": mr.local_voluntary,
                        "regional_voluntary": mr.regional_voluntary,
                        "national_voluntary": mr.national_voluntary,
                    }
                )

            # save local only
            if new_code not in [
                "supporter",
                "former_supporter",
                "member_candidate",
                "member_committee",
                "member",
                "former_member",
                "former_member_committee",
            ]:
                partner_values["local_only"] = mr.local_only

            self._validate_request_coordinates(mr, partner_values)

            if (
                mr.result_type_id != mr.membership_state_id
                or mr.force_int_instance_id != partner.int_instance_ids
                or mr.int_instance_ids != partner.int_instance_ids
            ):
                mr._validate_request_membership(mr, partner)
            # address if technical name is empty then means that no address
            # required
            mr.technical_name = mr.get_technical_name(
                mr.address_local_street_id.id,
                mr.city_id.id,
                mr.number,
                mr.box,
                mr.city_man,
                mr.street_man,
                mr.zip_man,
                mr.country_id.id,
            )
            mr.onchange_technical_name()
            address_id = mr.address_id and mr.address_id.id or False
            if (
                not address_id
                and mr.technical_name
                and mr.technical_name != EMPTY_ADDRESS
            ):
                address_values = {
                    "country_id": mr.country_id.id,
                    "street_man": False
                    if mr.address_local_street_id
                    else mr.street_man,
                    "zip_man": False if mr.city_id else mr.zip_man,
                    "city_man": False if mr.city_id else mr.city_man,
                    "address_local_street_id": mr.address_local_street_id
                    and mr.address_local_street_id.id
                    or False,
                    "city_id": mr.city_id and mr.city_id.id or False,
                    "street2": mr.street2,
                    "number": mr.number,
                    "box": mr.box,
                    "sequence": mr.sequence,
                }
                address_id = mr.env["address.address"].create(address_values)
                mr_vals["address_id"] = address_id
            partner_values.update({"address_address_id": address_id})

            if partner_values:
                partner.write(partner_values)

        # if request `validate` then object should be invalidate
        mr_vals.update({"state": "validate"})

        # superuser_id because of record rules
        self.sudo().action_invalidate(vals=mr_vals)
        return True

    @api.model
    def _validate_request_membership(self, mr, partner):
        active_memberships = partner.membership_line_ids.filtered(lambda s: s.active)
        if mr.force_int_instance_id:
            # we want only one instance
            active_memberships.filtered(
                lambda s, i=mr.force_int_instance_id: s.int_instance_id != i
            )._close(force=True)

        for instance in mr.force_int_instance_id or mr.int_instance_ids:
            membership_instance = active_memberships.filtered(
                lambda s, i=instance: s.int_instance_id == i
            )
            if mr.result_type_id.code != "without_membership" and (
                not membership_instance
                or membership_instance.state_id != mr.result_type_id
            ):
                if active_memberships:
                    active_memberships._close(force=True)
                    active_memberships.flush()
                    w = self.env["add.membership"].create(
                        {
                            "int_instance_id": instance.id,
                            "partner_id": partner.id,
                            "product_id": membership_instance.product_id.id,
                            "state_id": mr.result_type_id.id,
                            "price": 0,
                        }
                    )
                else:
                    w = self.env["add.membership"].create(
                        {
                            "int_instance_id": instance.id,
                            "partner_id": partner.id,
                            "product_id": partner.subscription_product_id.id,
                            "state_id": mr.result_type_id.id,
                        }
                    )
                    w._onchange_product_id()  # compute the price
                w.action_add()

                active_memberships = partner.membership_line_ids.filtered(
                    lambda s: s.active
                )
                # save membership amount
                if mr.amount > 0.0 and mr.reference:
                    product = self.env["product.product"].search(
                        [
                            ("membership", "=", True),
                            ("list_price", "=", mr.amount),
                        ],
                        limit=1,
                    )
                    vals = {
                        "reference": mr.reference,
                        "price": mr.amount,
                    }
                    if product:
                        vals["product_id"] = product.id
                    active_memberships.write(vals)

    @api.model
    def _validate_request_involvement(self, mr, partner):
        current_categories = partner.partner_involvement_ids.mapped(
            "involvement_category_id"
        )
        new_categories = mr.involvement_category_ids.filtered(
            lambda s, cc=current_categories: s not in cc or s.allow_multi
        )
        for ic in new_categories:
            vals = {
                "partner_id": partner.id,
                "effective_time": mr.effective_time,
                "involvement_category_id": ic.id,
            }
            if ic.involvement_type == "donation":
                vals.update(
                    {
                        "reference": mr.reference,
                        "amount": mr.amount,
                    }
                )
            self.env["partner.involvement"].create(vals)

    @api.model
    def _validate_request_coordinates(self, mr, partner_values):
        # case of email
        if mr.email:
            partner_values["email"] = mr.email
        # case of phone
        if mr.phone:
            partner_values["phone"] = mr.phone
        # case of mobile
        if mr.mobile:
            partner_values["mobile"] = mr.mobile

    def cancel_request(self):
        # superuser_id because of record rules
        self.sudo().action_invalidate(vals={"state": "cancel"})
        return True

    def _get_instance_partner(self, partner_values):
        """
        If the membership request concerns a new partner and if an internal instance
        is present on the membership request, we use it to force the instance
        of the partner.
        """
        self.ensure_one()
        if not self.partner_id and self.force_int_instance_id:
            partner_values.update(
                {"force_int_instance_id": self.force_int_instance_id.id}
            )
        elif not self.partner_id and self.int_instance_ids:
            partner_values.update({"force_int_instance_id": self.int_instance_ids.id})

    @api.model
    def get_int_instance_id(self, city_id):
        """
        :rtype: integer
        :rparam: instance id of address local zip or default instance id if
            `address_local_zip_id` is False
        """
        if city_id:
            zip_obj = self.env["res.city"]
            zip_rec = zip_obj.browse(city_id)
            return zip_rec.int_instance_id.id
        else:
            instance_obj = self.env["int.instance"]
            return instance_obj._get_default_int_instance().id

    @api.model_create_single
    def create(self, vals):
        # Automatically correct case errors in firstname and lastname
        # Will not be corrected in write() so user can bypass
        # this modification.
        for key in ["lastname", "firstname"]:
            val = vals.get(key, False)
            if val:
                vals[key] = val.strip().title()
        if self.env.context.get("install_mode", False) or self.env.context.get(
            "mode", True
        ) in ["ws", "pre_process"]:
            self._pre_process(vals)

        # do not pass related fields to the orm
        self._pop_related(vals)
        if "day" in vals and "month" in vals and "year" in vals:
            vals["birthdate_date"] = self.get_birthdate_date(
                vals.get("day"), vals.get("month"), vals.get("year")
            )
        request_id = super().create(vals)
        request_id._detect_changes()

        return request_id

    def write(self, vals):
        # do not pass related fields to the orm
        active_ids = self.search([("id", "in", self.ids), ("active", "=", True)])
        self._pop_related(vals)
        # we need to recompute the day since it's readonly
        if "day" in vals or "month" in vals or "year" in vals:
            for req in self:
                vals["birthdate_date"] = self.get_birthdate_date(
                    vals.get("day", req.day),
                    vals.get("month", req.month),
                    vals.get("year", req.year),
                )
        res = super().write(vals)
        if "active" in vals:
            if not vals.get("active"):
                active_ids = []
        if active_ids:
            active_ids._detect_changes()
        return res

    def name_get(self):
        """
        display name is `lastname firstname`
        **Note**
        if firstname is empty then it is just lastname alone
        """
        res = []
        for record in self:
            display_name = (
                "%s" % record.lastname
                if not record.firstname
                else "%s %s" % (record.lastname, record.firstname)
            )
            res.append((record["id"], display_name))
        return res
