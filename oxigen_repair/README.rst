=============
Oxigen Repair
=============

* This module makes operations and fee_lines editable in Repair Orders
* If RO in under_repair or cancelled states, it can be set again to draft
* New fields: km, list_date
* Cannot delete/cancel a finished Repair Order (state Done or To be Invoiced)
* If there is an unfinished RO with a certain product and lot, a new one for the same lot can't be created until the previous one is finished.
* Cannot add Parts/Operations in RO if no Customer is defined
* New button in product template/variant to see Repairs where the product appears as a Part

Credits
=======

Contributors
------------

* Maria de Luna <maria.de.luna@forgeflow.com>
