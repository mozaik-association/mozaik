# -*- encoding: utf-8 -*-

__name__ = 'Delete IR_UI_VIEW where parent_id has been deleted'


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "DELETE FROM ir_ui_view "
        "WHERE name like 'partner.view.buttons (mozaik_account)'"
    )
