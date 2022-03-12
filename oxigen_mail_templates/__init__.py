from openupgradelib import openupgrade


def _pre_init_hook(cr):
    cr.execute(
        """
        SELECT id, create_uid, write_uid, create_date, write_date
        FROM mail_template
        WHERE name = 'Lote de factura Oxigen Salud S.A.'
        """
    )
    data = cr.fetchone()
    if data:
        cr.execute(
            """
            INSERT INTO ir_model_data (module, name, model, res_id,
                create_uid, write_uid, create_date, write_date)
            VALUES ('oxigen_mail_templates', 'invoice_batch_email_template',
                'mail.template', %s, %s, %s, %s, %s)""",
            (data[0], data[1], data[2], data[3], data[4]),
        )
        cr.execute(
            """
            DELETE FROM ir_translation
            WHERE name LIKE 'mail.template,%%' AND res_id = %s""",
            (data[0],),
        )
