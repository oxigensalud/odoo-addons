from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "maintenance_equipment", "location_id"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "maintenance.equipment",
                    "maintenance_equipment",
                    "location_id",
                    "stock_location_id",
                ),
            ],
        )
    openupgrade.load_data(
        env.cr, "oxigen_maintenance", "migrations/14.0.1.1.0/noupdate_changes.xml"
    )
