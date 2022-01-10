# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


class TestOxigenMaintenance(common.TransactionCase):
    def setUp(self):
        super(TestOxigenMaintenance, self).setUp()
        self.env = self.env(
            context=dict(
                self.env.context,
                tracking_disable=True,
            )
        )
        self.maintenance_request_obj = self.env["maintenance.request"]
        self.maintenance_plan_obj = self.env["maintenance.plan"]
        self.maintenance_equipment_obj = self.env["maintenance.equipment"]
        self.cron = self.env.ref("maintenance.maintenance_requests_cron")
        self.weekly_kind = self.env.ref("maintenance_plan.maintenance_kind_weekly")
        self.weekly_kind.name = "Weekly"

        self.equipment_1 = self.maintenance_equipment_obj.create({"name": "Laptop 1"})
        today = fields.Date.today()
        self.today_date = fields.Date.from_string(today)
        self.maintenance_plan_1 = self.maintenance_plan_obj.create(
            {
                "name": "Test Plan",
                "equipment_id": self.equipment_1.id,
                "start_maintenance_date": today,
                "interval": 1,
                "maintenance_kind_id": self.weekly_kind.id,
                "interval_step": "week",
                "maintenance_plan_horizon": 1,
                "planning_step": "week",
            }
        )

        self.maintenance_plan_2 = self.maintenance_plan_obj.create(
            {
                "equipment_id": self.equipment_1.id,
                "interval": 1,
                "interval_step": "month",
                "maintenance_plan_horizon": 2,
                "planning_step": "month",
            }
        )
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.location_1 = self.env["stock.location"].create(
            {
                "name": "Test location 1",
                "usage": "internal",
                "location_id": self.stock_location.id,
            }
        )

    def test_01_maintenance_request_name(self):
        self.cron.method_direct_trigger()
        generated_requests = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_1.id)],
            order="schedule_date asc",
        )
        self.assertEqual(len(generated_requests), 2)

        self.assertEqual(generated_requests[0].name, "Weekly - Laptop 1 - Test Plan")

    def test_02_equipment_location(self):
        self.equipment_1.location_id = self.location_1.id
        self.assertEqual(self.location_1.equipment_ids.id, self.equipment_1.id)

    def test_03_maintenance_plan_employee(self):
        self.employee = self.env["hr.employee"].create({"name": "David Employee"})
        self.maintenance_plan_2.employee_id = self.employee.id
        self.cron.method_direct_trigger()

        generated_requests_1 = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_1.id)],
            order="schedule_date asc",
        )
        generated_requests_2 = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_2.id)],
            order="schedule_date asc",
        )
        self.assertEqual(len(generated_requests_2), 3)

        self.assertEqual(
            generated_requests_1[0].employee_id.id,
            self.env["hr.employee"]
            .search([("user_id", "=", self.env.uid)], limit=1)
            .id,
        )
        self.assertEqual(generated_requests_2[0].employee_id.id, self.employee.id)
