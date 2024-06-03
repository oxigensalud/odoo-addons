# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "oxigen_maintenance",
        [
            "only_subscribe_user",
            "only_subscribe_manager",
            "equipment_rule_user",
            "equipment_rule_manager",
        ],
        False,
    )

    openupgrade.load_data(
        env.cr,
        "oxigen_maintenance",
        "security/security.xml",
    )

    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "oxigen_maintenance.group_maintenance_user",
            "oxigen_maintenance.group_maintenance_manager",
        ],
    )

    env.ref("maintenance.group_equipment_manager").write(
        {
            "category_id": env.ref("base_maintenance_group.module_maintenance").id,
            "implied_ids": [
                (4, env.ref("base_maintenance_group.group_maintenance_user").id)
            ],
        }
    )
