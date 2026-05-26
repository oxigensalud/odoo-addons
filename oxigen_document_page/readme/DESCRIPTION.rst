This module bundles Oxigen-specific customizations on document pages.

Reference auto-generation
-------------------------

Changes how the ``reference`` field is auto-filled. By default, the OCA module
``document_page_reference`` generates a new reference from a slug of the
document title. For environments migrating from a legacy DMS such as KmKEY —
where each document has a 10-digit numeric Id — this default is unsuitable.

With this module installed:

* When a new document page is created without a ``reference``, the field is
  auto-filled with a random unique numeric code of 10 digits.
* When a ``reference`` is provided manually (for example to preserve a legacy
  KmKEY Id during migration), it is left untouched.
* Existing document pages keep their current reference.
* Uniqueness is enforced via the existing ``_check_reference`` constraint.

Archive wizard with mandatory reason
------------------------------------

Replaces the one-click ``Archive`` / ``Unarchive`` action on document pages
with a wizard that requires the user to enter a reason. Every change of state
on a controlled document is logged in the chatter with who changed it and why.
