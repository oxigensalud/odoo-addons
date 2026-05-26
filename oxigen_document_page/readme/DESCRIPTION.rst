This module changes how the ``reference`` field of document pages is auto-filled.

By default, the OCA module ``document_page_reference`` generates a new reference
from a slug of the document title (e.g. ``i_t_108_01_documentacion_y_liberacion``).
For environments migrating from a legacy DMS such as KmKEY — where each document
has a 10-digit numeric Id — this default is unsuitable.

With this module installed:

* When a new document page is created without a ``reference``, the field is
  auto-filled with a random unique numeric code of 10 digits.
* When a ``reference`` is provided manually (for example to preserve a legacy
  KmKEY Id during migration), it is left untouched.
* Existing document pages keep their current reference.
* Uniqueness is enforced via the existing ``_check_reference`` constraint.

Caveat: documents whose reference is purely numeric cannot be targeted by the
``${ref}`` Jinja link mechanism of ``document_page_reference``, because Jinja
parses a pure-digit ``${...}`` expression as an integer literal instead of a
variable lookup. Alphabetical references keep working as before.
