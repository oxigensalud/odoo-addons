# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestMaintenanceSecurity(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
            )
        )
        cls.admin = cls.env["res.users"].create(
            {
                "name": "Admin",
                "login": "admin_demo",
                "groups_id": [
                    (4, cls.env.ref("oxigen_maintenance.group_maintenance_manager").id),
                    (4, cls.env.ref("base.group_user").id),
                ],
            }
        )
        cls.manager = cls.env["res.users"].create(
            {
                "name": "Manager",
                "login": "manager_demo",
                "groups_id": [
                    (4, cls.env.ref("maintenance.group_equipment_manager").id),
                    (4, cls.env.ref("base.group_user").id),
                ],
            }
        )
        cls.maintenance_user = cls.env["res.users"].create(
            {
                "name": "maintenance_user",
                "login": "maintenance_user_demo",
                "groups_id": [
                    (4, cls.env.ref("oxigen_maintenance.group_maintenance_user").id),
                    (4, cls.env.ref("base.group_user").id),
                ],
            }
        )
        cls.user = cls.env["res.users"].create(
            {
                "name": "User",
                "login": "user_demo",
                "groups_id": [(4, cls.env.ref("base.group_user").id)],
            }
        )
        cls.team_01 = cls.env["maintenance.team"].create(
            {
                "name": "Team 01",
                "member_ids": [(4, cls.maintenance_user.id)],
            }
        )
        cls.team_02 = cls.env["maintenance.team"].create(
            {
                "name": "Team 02",
                "member_ids": [(4, cls.manager.id)],
            }
        )
        cls.equipment_00 = cls.env["maintenance.equipment"].create(
            {
                "name": "Equipment No team",
            }
        )
        cls.equipment_01 = cls.env["maintenance.equipment"].create(
            {
                "name": "Equipment 1",
                "maintenance_team_id": cls.team_01.id,
            }
        )
        cls.equipment_02 = cls.env["maintenance.equipment"].create(
            {
                "name": "Equipment 2",
                "maintenance_team_id": cls.team_02.id,
            }
        )

    def test_security(self):
        self.assertTrue(
            self.equipment_00.with_user(self.maintenance_user.id).my_team_equipment
        )
        self.assertTrue(
            self.equipment_01.with_user(self.maintenance_user.id).my_team_equipment
        )
        self.assertFalse(
            self.env["maintenance.equipment"]
            .with_user(self.maintenance_user.id)
            .search([("id", "=", self.equipment_02.id)])
        )
        self.assertIn(
            self.equipment_00,
            self.env["maintenance.equipment"]
            .with_user(self.maintenance_user.id)
            .search([("my_team_equipment", "=", True)]),
        )
        self.assertIn(
            self.equipment_01,
            self.env["maintenance.equipment"]
            .with_user(self.maintenance_user.id)
            .search([("my_team_equipment", "=", True)]),
        )
        self.assertTrue(self.equipment_00.with_user(self.manager.id).my_team_equipment)
        self.assertFalse(
            self.env["maintenance.equipment"]
            .with_user(self.manager.id)
            .search([("id", "=", self.equipment_01.id)])
        )
        self.assertTrue(self.equipment_02.with_user(self.manager.id).my_team_equipment)
        self.assertIn(
            self.equipment_00,
            self.env["maintenance.equipment"]
            .with_user(self.manager.id)
            .search([("my_team_equipment", "=", True)]),
        )
        self.assertIn(
            self.equipment_02,
            self.env["maintenance.equipment"]
            .with_user(self.manager.id)
            .search([("my_team_equipment", "=", True)]),
        )
