# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os

from odoo import api, models, tools
from odoo.modules import get_module_resource
from odoo.osv import expression
from odoo.tools.translate import PoFileReader


def _po_files(module_name):
    """The PO files of the module in the folders the translation loader reads,
    with the language code their name gives."""
    po_files = []
    for folder in ("i18n", "i18n_extra"):
        path = get_module_resource(module_name, folder)
        names = sorted(os.listdir(path)) if path else []
        po_files += [
            (os.path.splitext(name)[0], os.path.join(path, name))
            for name in names
            if name.endswith(".po")
        ]
    return po_files


def _loaded_langs(code, langs):
    """The languages among ``langs`` for which the translation loader reads the
    PO files named ``code``: those of their ISO code, and of its base for a
    regional language (``ir.translation._load_module_terms``)."""
    iso_codes = {lang: tools.get_iso_codes(lang) for lang in langs}
    return [
        lang
        for lang, iso_code in iso_codes.items()
        if code in (iso_code, iso_code.split("_")[0])
    ]


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    @api.model
    def _module_terms(self, module_name):
        """Return the translations of the texts that the PO files of
        ``module_name`` translate, as a set of ``(language, "<model>,<field>",
        record)``: in each installed language the loader reads one of those
        files for, and in English, since the English of those texts is the
        text of the record itself. A text whose record no longer exists, such
        as a stock formula a manager deleted, is left out: there is nothing to
        force or give back for it, and an install never meets one, because its
        data file fails first on the missing record."""
        installed = [lang for lang, _name in self.env["res.lang"].get_installed()]
        terms = set()
        for code, path in _po_files(module_name):
            langs = _loaded_langs(code, installed) + ["en_US"]
            for entry in PoFileReader(path):
                # The loader skips empty translations
                if entry["type"] == "model" and entry["value"]:
                    record = self.env.ref(
                        "%s.%s" % (entry["module"], entry["imd_name"]),
                        raise_if_not_found=False,
                    )
                    if record is not None:
                        terms.update((lang, entry["name"], record) for lang in langs)
        return terms

    @api.model
    def _delete_module_terms(self, module_name):
        """Delete the stored translations of the module's terms
        (``_module_terms``)."""
        terms = self._module_terms(module_name)
        self.search(
            [("type", "=", "model")]
            + expression.OR(
                [
                    [
                        ("lang", "=", lang),
                        ("name", "=", name),
                        ("res_id", "=", record.id),
                    ]
                    for lang, name, record in terms
                ]
            )
        ).unlink()
        # An unlink that deletes rows invalidates the whole cache, one that finds
        # none invalidates nothing, and the PO files are loaded through SQL:
        # the translated values of the records are invalidated here
        for _lang, name, record in terms:
            record.invalidate_cache([name.split(",")[1]], record.ids)

    @api.model
    def _force_module_terms(self, module_name):
        """Give the records that the PO files of ``module_name`` translate the
        translations of those files, over the ones stored. Loading the files
        alone is not enough: without overwrite the importer keeps every stored
        translation, and even with overwrite it never updates the stored
        translation of a ``noupdate`` record, only inserts a missing one."""
        self._delete_module_terms(module_name)
        module = self.env["ir.module.module"].search([("name", "=", module_name)])
        module.ensure_one()
        module._update_translations()
