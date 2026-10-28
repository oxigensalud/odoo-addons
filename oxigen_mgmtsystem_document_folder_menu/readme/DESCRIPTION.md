At 18.0, OCA's management system modules select the documents of the
*Procedures*, *Environmental Aspects*, *Work Instructions* and
*Manuals* menus by management system page type, wherever they are in
the folder tree, instead of listing the folders and pages placed
directly under each menu's base category. This module gives the four
menus back that 14.0 list, so that the documents are browsed folder by
folder.

It changes the domain of the four menus' actions. For *Manuals* it
also gives back the default category that OCA's 18.0 action dropped,
so a page created from that menu is placed in it and stays in its
list. The other contexts and every view are OCA's.

The module installs itself (`auto_install`) together with the four
modules it depends on. A database migrated from 14.0, where it did not
exist, gets it when OpenUpgrade migrates it to 18.0, since OpenUpgrade
installs the `auto_install` modules whose dependencies are installed.
On a database that already has the four modules, outside a migration,
it is installed by hand.
