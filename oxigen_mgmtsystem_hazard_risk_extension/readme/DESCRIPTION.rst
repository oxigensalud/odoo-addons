This module presents the third factor of the hazard risk evaluation as
*Detectability* instead of *Occupation / Usage*, in English, Spanish and
Catalan:

* in the label of the factor on hazards and on residual risks, and in the label
  of the name of its values;
* in the name of the configuration menu that lists those values, and of its
  action: both records belong to ``mgmtsystem_hazard``, and this module
  overrides their name;
* in the description of the four stock risk formulas that use the third
  factor.

It changes no technical field, no formula and no risk calculation.

When the module is installed, these texts get its wording in English, Spanish
and Catalan, whatever translations were stored for them. They get it again each
time a language is loaded or updated with *Load a Translation*, which can
otherwise bring back the wording of the dependencies.

When the module is uninstalled, the four formulas get back their stock English
description, unless it was edited in the meantime, its translations of these
texts are deleted, and the translation files of the three modules it depends on
are loaded again for every installed language, as an update of them does: what
this module deleted comes back wherever they translate it, and the stored
translations are kept, apart from what Odoo's loader writes over them from a
regional file, such as the Catalan of ten common field labels from the
``ca_ES.po`` of ``mgmtsystem_hazard``. What comes back only with an update of
the dependencies is listed under *Known issues / Roadmap*.
