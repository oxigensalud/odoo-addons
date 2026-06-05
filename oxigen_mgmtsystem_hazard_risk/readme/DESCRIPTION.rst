This module adapts the third factor of the hazard risk evaluation so it is
presented to the user as *Detectability* instead of *Occupation / Usage*.

To keep the wording consistent across languages, the change is applied at the
English source: the field labels are redefined through inheritance, the
action, menu, form title and search title for the master-data list are
renamed, and the source text of the four formula descriptions that mention
the third factor is updated. On top of that, the risk computation
description is made translatable so the formula text can be localized as a
complete phrase in Catalan and Spanish.

The addon does not change the technical field name, formulas, XML IDs, views
or risk calculation behavior. An uninstall hook restores the upstream
wording on removal, and preserves any value the user may have customized
manually.
