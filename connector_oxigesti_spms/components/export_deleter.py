from odoo.addons.component.core import AbstractComponent


class ConnectorExtensionRecordDirectExportDeleter(AbstractComponent):
    _name = "oxigesti.spms.record.direct.export.deleter"
    _inherit = [
        "connector.extension.record.direct.export.deleter",
        "oxigesti.spms.connector",
    ]


class ConnectorExtensionBatchExportDeleter(AbstractComponent):
    _name = "oxigesti.spms.batch.export.deleter"
    _inherit = [
        "connector.extension.batch.export.deleter",
        "oxigesti.spms.connector",
    ]


class ConnectorExtensionBatchtDirectExportDeleter(AbstractComponent):
    _name = "oxigesti.spms.batch.direct.export.deleter"
    _inherit = [
        "connector.extension.batch.direct.export.deleter",
        "oxigesti.spms.connector",
    ]


class ConnectorExtensionBatchDelayedExportDeleter(AbstractComponent):
    _name = "oxigesti.spms.batch.delayed.export.deleter"
    _inherit = [
        "connector.extension.batch.export.deleter",
        "oxigesti.spms.connector",
    ]
