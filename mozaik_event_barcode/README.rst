====================
Mozaik Event Barcode
====================

* Adds barcodes on event.registration records.
* Adds a button from event.event form view to access a page from where the event organizer can scan barcodes to confirm the attendance of the partners. Alternatively, a membership card (attendee's identifier) can be scanned instead of a barcode.
* Adds the option to activate a **Voting Domain** on event.events, to compute which attendees can vote at the event.
* Show in the barcode scanner wizard if the partner can vote or not.

Voting Domain Features
======================

1. On the Event "Voting Domain" page, tick "Is Voting Domain Required" to activate the voting domain. If not ticked, the option is not activated, and all partners on registrations will be marked as `can_vote = False`.
2. When ticked, configure the voting domain by defining a domain on the virtual Partner/Membership model.
3. When a partner registers to the event, the voting domain is checked, and the `can_vote` boolean on the registration is ticked accordingly.
4. If the voting domain is updated and if the `can_vote` boolean must be recomputed on existing registrations, click on the **Recompute voting domain** button on the event. Note that the computation can be long, this is why the recompute isn't triggered automatically.

Technical
---------
The `is_voting_domain_required` checkbox was added to inactivate the feature, otherwise the default empty domain on virtual.partner.membership
caused some slowness when computing the `can_vote` boolean, because of the mapping between the virtual model and the res.partner model.
See https://acsone.plan.io/issues/85088 for details.

