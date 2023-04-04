# Membership

## Membership line
It is possible to follow-up the membership history of a member from the memberships tab of a contact. In this tab, you can find a whole list of information:

- Internal instance to which the member is linked by its membership.
- Membership status to which the contact belongs (former member, new member...).
- Type of membership fee paid (normal membership, reduce price (job seeker, disabled)).
- Price of the subscription.
- Structured communication reference (possible to work with a structured communication).
- Payement link (possible to pay the membership online with Stripe, Adyen...)
- Check whether the member is in good standing or not.
- Start and end date of the membership.

This tab provides you to easily manage or modify memberships. 

Mozaik provides you to manage the membership cards of the organisation, to see who has already received his card and who has not yet received it.
 
Each member in Odoo is linked to a unique member number. The member number can be found on the contact form next to the contacts name and the membership state.

!!! abstract "The goal of membership lines"

    Membership lines provides you to follow-up the membership status of each contact as well as membership dates. You can easilly do some reporting by organising your members by membership states , local groups, type of memberships (prices), dates ,...
<figure markdown>
![screenshot 8](img/screen8.png)
<figcaption>New memberhsip line on the contact form & unique member number</figcaption>
</figure>

## Membership fees
Several membership types can be added in Mozaik. Each organisation can define its own membership types and link each type to a specific price and rule. Members will have to pay a specific price according to these rules.

!!! example

    1. It is possible to set a lower price for the first year of membership compared to subsequent years.
    2. It is possible to put a different price for people with disabilities (example: 5€ instead of 10€)

!!! abstract "The goal of memberships fees"

    The purpose of this feature is to allow prices and membership types to be adapted to the specificities of the organisation's contacts.
        

<figure markdown>
![screenshot 32](img/screen32.png)
<figcaption>Creation of different types of subscriptions</figcaption>
</figure>

## Membership Statuses

A complete membership workflow has been implemented in Mozaik. Members are linked to a membership status that evolves over time according to certain rules.
!!! info

    This workflow can easily be adapted if it does not meet the exact needs of the organisation.

<figure markdown>
![screenshot 9](img/screen9.png)
<figcaption>Example of the different membership statuses of an organisation</figcaption>
</figure>
!!! example "Example of workflow"

    - A member who resigns changes from a "member" to a "resignation former member".
    - A member who declines to pay the membership fee will be given the status "former member".
<figure markdown>
![screenshot 10](img/screen10.png)
<figcaption>Mozaik memberships workflow</figcaption>
</figure>


## Membership renewals
Each year, the organisation may issue a call for membership renewal. Members who did not pay the previous year become " former members ".

Members in good standing will receive:

- An email with a link to pay online. 
- A letter with a structured communication to pay.

!!!info

    It is possible to change the status of all members who have not paid their membership fee before the deadline to "former member fee".
<figure markdown>
![screenshot 13](img/screen13.png)
<figcaption>Example of a membership renewal workflow</figcaption>
</figure>