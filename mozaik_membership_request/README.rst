=========================
Mozaik Membership Request
=========================

This is the core addon creating the membership requests.
Membership requests are created to (non-exhaustive list):
- Add a new contact to the database
- Update some personal data of a contact (address, personal info...)
- Add an involvement to a contact
- Become a member or a supporter
- ...

**Please note that this readme is currently under creation/improvement and is not complete.**

Usage
=====
To update the membership state of a member, please create a membership request of type "m".
Depending on the workflow, it can either close the existing membership line, to create a new one, or update the subscription product & price on an existing membership line.

Specific case of free memberships
---------------------------------
One may want to offer free memberships, for example for a dedicated time period.

The configuration is the following:

1. Create a specific subscription product under Contacts > Configuration > Subscriptions.
Please tick "Automatically create the following membership line" since your membership line will be automatically marked as paid, and you want your partner to progress in your membership workflow.

2. Create a membership tarification under Contacts > Configuration > Membership Tarification.
Please pay a particular attention to the `code` and `sequence` fields: `code` allows to define a domain to restrict which partners can have access to this product.
`sequence` allows to sort your tarifications. A free product shouldn't have a low sequence as it would be offered to all your partners.

3. Either follow the classical flow: the free product will be offered to partners verifying the domain given in `code` field of your tarification, or force the free product on the membership request.
The second option allows you to deactivate the automatic assignment of the free product (by setting a false domain into `code`, such as `0==1`), but force it on some membership requests under the `force_product_id` field.
NB: At the moment the field is only accessible via the code (to be used in API services for eg.).
