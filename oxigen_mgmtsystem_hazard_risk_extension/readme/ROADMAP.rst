* After the module is uninstalled, the three labels and the name of the menu
  and of its action keep this module's English wording, which every language
  the dependencies leave untranslated also shows: Catalan, and Portuguese for
  the label on residual risks, which ``mgmtsystem_hazard_risk`` translates
  into Brazilian Portuguese only. The original wording comes back when
  ``mgmtsystem_hazard`` and ``mgmtsystem_hazard_risk`` are updated by hand
  (``-u``); Odoo then also updates every installed module that depends on them,
  which is why the uninstall does not do it. Spanish comes back at once.
* The uninstall loads the translation files of ``mgmtsystem_hazard`` again, as
  an update of that module does, and Odoo's loader writes its regional file
  ``ca_ES.po`` over the stored translations: a Catalan edited by hand on ten
  common field labels of its models, such as *Company* and *Created by*, is
  replaced by that file's.
* Only the four stock formulas that use the third factor are relabelled: a
  formula created by a user keeps its own description.
* Only Spanish and Catalan are translated. In another language, the texts the
  dependencies translate keep their wording and the others show this module's
  English wording.
* The description of the model, *Usage of hazard*, is not changed.
* A translation of one of these texts edited by hand, in Spanish or Catalan, or
  in English for a label, is replaced when the module is installed, when a
  language is loaded and when the module is uninstalled. An English edit of the
  name of the menu, of its action or of a formula, made while the module is
  installed, is kept.
* A translation file imported with the overwrite option, with *Import
  Translation* or with ``--i18n-import`` and ``--i18n-overwrite``, replaces
  this module's Spanish or Catalan wording of the three labels and of the name
  of the menu and of its action, if it translates them, until a language is
  loaded again.
* Installing ``mgmtsystem_hazard_risk`` again (``-i``) on a database where it
  is installed resets the English description of the four formulas to the
  stock one, until this module is installed again: an update of this module
  (``-u``) does not rewrite them.
