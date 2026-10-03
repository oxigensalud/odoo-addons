This module adapts the OCA management system **Reviews** entity so it acts as
the company's **change control record**, following its change-control form,
without building a dedicated model.

It is a client-specific, cosmetic adaptation on top of the generic behaviour
added by ``mgmtsystem_review_copy_lines`` (duplicating a review copies its
lines, so a template record can be reused):

* hides the *Reviews* menu and adds a *Change Control Record* action and menu
  in its place,
* relabels the form (the name as the change subject, the lines tab as the
  change control sections, the conclusion as effectiveness / closure), the
  reference as the change control number in the form and the list, and the
  lines as sections with their content,
* hides the *Inputs* tab (policy, changes and surveys), which does not apply to
  change control.

Each change control is recorded as a review whose lines hold the sections of
the company's change-control form (description, reason, scope, type,
implementation plan, approvals, execution, closure, …). The creator, number,
date, participants and attached documents are the native review fields.
