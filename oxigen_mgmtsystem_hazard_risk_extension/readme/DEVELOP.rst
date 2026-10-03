``i18n/`` holds only this module's two own terms, *Detectability* and
*Detectabilities*: an export of the module also gives the names and three
standard field labels of the five models it extends, under this module's ids,
and those entries must be dropped, because ``_module_terms`` would force them
and the uninstall would delete their Spanish and Catalan translations, of which
the dependencies give back only those of their own models.
