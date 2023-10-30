from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
    UPDATE maintenance_equipment me
    SET name = it.value
    FROM ir_translation it
    WHERE it.name = 'maintenance.equipment,name' and it.lang = 'es_ES' AND me.id = it.res_id
    """,
    )
