# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.queue_job.job import DEFAULT_MAX_RETRIES
from odoo.addons.queue_job.tests.common import trap_jobs

from ..models.oxigesti_binding.common import MAX_RETRIES_NETWORK


@tagged("post_install", "-at_install")
class TestWithDelayMaxRetries(TransactionCase):
    """The ``retry_pattern`` declared on every oxigesti ``queue.job.function``
    (``{1: 10, 5: 30, 10: 60, 15: 300}``) is designed for up to ~20 attempts.
    OCA queue_job's ``DEFAULT_MAX_RETRIES`` is 5, which clipped every
    oxigesti job at the first bucket (10s x 4 = ~40s window) and turned the
    longer buckets (30s, 60s, 300s) into dead code.

    This test suite pins the override on ``OxigestiBinding.with_delay`` that
    defaults ``max_retries`` to ``MAX_RETRIES_NETWORK`` (20) so the declared
    pattern actually runs, giving a ~33-minute retry window per job —
    enough to absorb transient MSSQL restarts, VPN blips and short planned
    maintenance on the Oxigesti server.
    """

    def _enqueued_job(self, model, **with_delay_kwargs):
        """Delay a job on ``model`` and return it as queue_job built it.

        The job is trapped, never stored nor performed, so any job method of
        the binding does; ``import_batch`` exists on every oxigesti binding.
        """
        with trap_jobs() as trap:
            self.env[model].with_delay(**with_delay_kwargs).import_batch(
                self.env["oxigesti.backend"]
            )
        trap.assert_jobs_count(1)
        return trap.enqueued_jobs[0]

    def test_default_max_retries_matches_oxigesti_constant(self):
        """Without an explicit ``max_retries=``, the oxigesti binding must
        inject ``MAX_RETRIES_NETWORK`` (20) instead of the OCA default (5)."""
        job = self._enqueued_job("oxigesti.res.partner")
        self.assertEqual(job.max_retries, MAX_RETRIES_NETWORK)

    def test_explicit_max_retries_is_respected(self):
        """An explicit ``max_retries=N`` on the call site must win over the
        oxigesti default — e.g. for one-shot diagnostic enqueues."""
        job = self._enqueued_job("oxigesti.res.partner", max_retries=7)
        self.assertEqual(job.max_retries, 7)

    def test_explicit_zero_max_retries_is_respected(self):
        """``max_retries=0`` means infinite retries in queue_job — the
        oxigesti default must not silently replace it with 20."""
        job = self._enqueued_job("oxigesti.res.partner", max_retries=0)
        self.assertEqual(job.max_retries, 0)

    def test_other_kwargs_forwarded(self):
        """The override must pass ``priority``, ``eta``, ``description``,
        ``channel`` and ``identity_key`` through to the parent ``with_delay``
        untouched."""
        job = self._enqueued_job(
            "oxigesti.res.partner",
            priority=42,
            description="probe",
            channel="root.oxigesti",
            identity_key="probe-identity",
        )
        self.assertEqual(job.priority, 42)
        self.assertEqual(job.description, "probe")
        self.assertEqual(job.channel, "root.oxigesti")
        self.assertEqual(job.identity_key, "probe-identity")
        # And the injected default is still there alongside them.
        self.assertEqual(job.max_retries, MAX_RETRIES_NETWORK)

    def test_default_applied_to_multiple_binding_models(self):
        """The override lives on the abstract ``oxigesti.binding`` model, so
        every concrete binding (partners, products, lots, sale orders, etc.)
        must inherit the same default without per-model wiring."""
        for model in (
            "oxigesti.res.partner",
            "oxigesti.product.product",
            "oxigesti.stock.lot",
            "oxigesti.sale.order",
        ):
            with self.subTest(model=model):
                job = self._enqueued_job(model)
                self.assertEqual(job.max_retries, MAX_RETRIES_NETWORK)

    def test_non_oxigesti_model_keeps_oca_default(self):
        """The override must be scoped to oxigesti bindings — generic Odoo
        models (e.g. ``res.partner``) keep the OCA ``DEFAULT_MAX_RETRIES``
        that queue_job sets on the job when ``max_retries`` is not given."""
        with trap_jobs() as trap:
            self.env["res.partner"].with_delay().create({"name": "probe"})
        trap.assert_jobs_count(1)
        self.assertEqual(trap.enqueued_jobs[0].max_retries, DEFAULT_MAX_RETRIES)
