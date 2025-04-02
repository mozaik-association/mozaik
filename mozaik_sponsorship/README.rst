==================
Mozaik Sponsorship
==================

This addon adds a mechanism to offer sponsored memberships. These ones can be free or not, but they must be sponsored by someone.

Configuration
=============
Please follows these steps:

1. Create a sponsorship subscription product (Contacts > Configuration > Subscriptions).
Pay attention to tick "Is Sponsorship Subscription" (only 1 sponsorship product is currently allowed) and "Automatically create the following membership line" if your sponsorship product is free.

2. Create a membership tarification for this product (Contacts > Configuration > Membership tarification).
The python code specifying the applicable domain should be something like `membership_request and membership_request.sponsor_id and membership_request.can_be_sponsored`.
Link the membership tarification to the sponsorship product.

Usage
=====

To create a sponsored membership, you have to:

1. Create a membership request of type "member";
2. Specify a sponsor under the "Payment" notebook page;
3. If you want to pay more than the sponsorship fee (which can be free), specify the amount over the sponsor field.

If the targeted partner can be sponsored, a new membership line will be created, or the existing membership line will be updated.

Note the following restrictions concerning partners that can be sponsored:
Partner can NOT be sponsored if

* he's a member or (former) member committee
* he's a former member (or former member break,...) and already has a sponsor

