- Uninstalling the module leaves the four menus listing by folder. They
  list by page type again once `document_page_procedure`,
  `document_page_environmental_aspect`, `document_page_work_instruction`
  and `mgmtsystem_manual` are updated by hand (`-u`), which writes
  OCA's domains back; Odoo then also updates every installed module
  that depends on them, which is why the uninstall does not do it. The
  uninstall itself gives the *Manuals* action back its default context,
  which no update writes.
