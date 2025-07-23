from odoo.addons.component.core import AbstractComponent


class ConnectorExtensionGenericRecordDirectExportDeleter(AbstractComponent):

    _name = "oxigesti.spms.generic.record.direct.export.deleter"
    _inherit = [
        "connector.extension.generic.record.direct.export.deleter",
        "oxigesti.spms.connector",
    ]


class ConnectorExtensionGenericBatchExportDeleter(AbstractComponent):

    _name = "oxigesti.spms.generic.batch.export.deleter"
    _inherit = [
        "connector.extension.generic.batch.export.deleter",
        "oxigesti.spms.connector",
    ]


class ConnectorExtensionBatchtDirectExportDeleter(AbstractComponent):

    _name = "oxigesti.spms.generic.batch.direct.export.deleter"
    _inherit = [
        "connector.extension.generic.batch.direct.export.deleter",
        "oxigesti.spms.connector",
    ]


class ConnectorExtensionBatchDelayedExportDeleter(AbstractComponent):

    _name = "oxigesti.spms.generic.batch.delayed.export.deleter"
    _inherit = [
        "connector.extension.generic.batch.export.deleter",
        "oxigesti.spms.connector",
    ]
