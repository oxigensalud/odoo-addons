This module adapts the OCA management system **Reviews** entity so it acts as
Oxigen's **change control record** (Registro de Control de Cambios), following
the client form F.P.100.01, without building a dedicated model.

It is a client-specific, cosmetic adaptation on top of the generic behaviour
added by ``mgmtsystem_review_copy_lines`` (duplicating a review copies its
lines, so a template record can be reused):

* renames the *Reviews* menu, action and views to *Change Control Record*,
* relabels the relevant fields (the reference as the change control number, the
  lines tab as the change control sections, the conclusion as effectiveness /
  closure),
* hides the *Inputs* tab (policy, changes and surveys), which does not apply to
  change control.

Each change control is recorded as a review whose lines hold the sections of
the F.P.100.01 form (description, reason, scope, type, implementation plan,
approvals, execution, closure, …). The creator, number, date, participants and
attached documents are the native review fields.

The exact field naming and whether some data should become dedicated fields is
intentionally left to be validated with the quality manager; this module is the
first, pragmatic version meant to be reviewed in use.
