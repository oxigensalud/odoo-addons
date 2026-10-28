# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase
from odoo.tools.safe_eval import safe_eval

from ..hooks import uninstall_hook


class TestDocumentFolderMenu(TransactionCase):
    def test_procedures_list_direct_children(self):
        procedures = self.env.ref(
            "document_page_procedure.document_page_group_procedure"
        )
        folder = self.env["document.page"].create(
            {"name": "Folder", "type": "category", "parent_id": procedures.id}
        )
        page = self.env["document.page"].create(
            {"name": "Page", "parent_id": procedures.id}
        )
        nested_page = self.env["document.page"].create(
            {"name": "Nested Page", "parent_id": folder.id}
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "document_page_procedure.action_procedures"
        )
        pages = self.env["document.page"].search(safe_eval(action["domain"]))
        self.assertIn(folder, pages)
        self.assertIn(page, pages)
        self.assertNotIn(nested_page, pages)

    def test_environmental_aspects_list_direct_children(self):
        environmental_aspects = self.env.ref(
            "document_page_environmental_aspect.document_page_group_environmental_aspect"
        )
        folder = self.env["document.page"].create(
            {
                "name": "Folder",
                "type": "category",
                "parent_id": environmental_aspects.id,
            }
        )
        page = self.env["document.page"].create(
            {"name": "Page", "parent_id": environmental_aspects.id}
        )
        nested_page = self.env["document.page"].create(
            {"name": "Nested Page", "parent_id": folder.id}
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "document_page_environmental_aspect.action_environmental_aspects"
        )
        pages = self.env["document.page"].search(safe_eval(action["domain"]))
        self.assertIn(folder, pages)
        self.assertIn(page, pages)
        self.assertNotIn(nested_page, pages)

    def test_work_instructions_list_direct_children(self):
        work_instructions = self.env.ref(
            "document_page_work_instruction.document_page_group_work_instructions"
        )
        folder = self.env["document.page"].create(
            {
                "name": "Folder",
                "type": "category",
                "parent_id": work_instructions.id,
            }
        )
        page = self.env["document.page"].create(
            {"name": "Page", "parent_id": work_instructions.id}
        )
        nested_page = self.env["document.page"].create(
            {"name": "Nested Page", "parent_id": folder.id}
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "document_page_work_instruction.work_instructions_action"
        )
        pages = self.env["document.page"].search(safe_eval(action["domain"]))
        self.assertIn(folder, pages)
        self.assertIn(page, pages)
        self.assertNotIn(nested_page, pages)

    def test_manuals_list_direct_children(self):
        manuals = self.env.ref("mgmtsystem_manual.manuals")
        folder = self.env["document.page"].create(
            {"name": "Folder", "type": "category", "parent_id": manuals.id}
        )
        page = self.env["document.page"].create(
            {"name": "Page", "parent_id": manuals.id}
        )
        nested_page = self.env["document.page"].create(
            {"name": "Nested Page", "parent_id": folder.id}
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mgmtsystem_manual.action_manuals"
        )
        pages = self.env["document.page"].search(safe_eval(action["domain"]))
        self.assertIn(folder, pages)
        self.assertIn(page, pages)
        self.assertNotIn(nested_page, pages)

    def test_manuals_create_page_in_manuals(self):
        manuals = self.env.ref("mgmtsystem_manual.manuals")
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mgmtsystem_manual.action_manuals"
        )
        page = (
            self.env["document.page"]
            .with_context(**safe_eval(action["context"]))
            .create({"name": "Page"})
        )
        pages = self.env["document.page"].search(safe_eval(action["domain"]))
        self.assertEqual(page.parent_id, manuals)
        self.assertIn(page, pages)


class TestUninstallHook(TransactionCase):
    def test_uninstall_gives_manuals_back_default_context(self):
        action = self.env.ref("mgmtsystem_manual.action_manuals")
        uninstall_hook(self.env)
        self.assertEqual(action.context, "{}")

    def test_uninstall_keeps_manuals_context_edited_by_hand(self):
        action = self.env.ref("mgmtsystem_manual.action_manuals")
        action.context = "{'default_type': 'content'}"
        uninstall_hook(self.env)
        self.assertEqual(action.context, "{'default_type': 'content'}")

    def test_uninstall_keeps_manuals_context_of_deleted_category(self):
        action = self.env.ref("mgmtsystem_manual.action_manuals")
        context = action.context
        self.env.ref("mgmtsystem_manual.manuals").unlink()
        uninstall_hook(self.env)
        self.assertEqual(action.context, context)
