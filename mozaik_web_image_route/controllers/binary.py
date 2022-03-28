# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http

from odoo.addons.web.controllers.main import Binary as BaseBinary


class Binary(BaseBinary):
    @http.route(
        [
            "/web/image_api",
            "/web/image_api/<string:xmlid>",
            "/web/image_api/<string:xmlid>/<string:filename>",
            "/web/image_api/<string:xmlid>/<int:width>x<int:height>",
            "/web/image_api/<string:xmlid>/<int:width>x<int:height>/<string:filename>",
            "/web/image_api/<string:model>/<int:id>/<string:field>",
            "/web/image_api/<string:model>/<int:id>/<string:field>/<string:filename>",
            "/web/image_api/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>",  # noqa: B950 pylint: disable=line-too-long
            "/web/image_api/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>/<string:filename>",  # noqa: B950 pylint: disable=line-too-long
            "/web/image_api/<int:id>",
            "/web/image_api/<int:id>/<string:filename>",
            "/web/image_api/<int:id>/<int:width>x<int:height>",
            "/web/image_api/<int:id>/<int:width>x<int:height>/<string:filename>",
            "/web/image_api/<int:id>-<string:unique>",
            "/web/image_api/<int:id>-<string:unique>/<string:filename>",
            "/web/image_api/<int:id>-<string:unique>/<int:width>x<int:height>",
            "/web/image_api/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>",  # noqa: B950 pylint: disable=line-too-long
        ],
        type="http",
        auth="public",
    )
    def content_image_api(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,  # pylint: disable=redefined-builtin
        field="datas",
        filename_field="name",
        unique=None,
        filename=None,
        mimetype=None,
        download=None,
        width=0,
        height=0,
        crop=False,
        access_token=None,
        **kwargs
    ):
        return super().content_image(
            xmlid,
            model,
            id,
            field,
            filename_field,
            unique,
            filename,
            mimetype,
            download,
            width,
            height,
            crop,
            access_token,
            **kwargs
        )
