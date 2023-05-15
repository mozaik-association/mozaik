# Accounting

The Mozaik accounting module offers some additional functionalities to the Odoo standard, which are particularly suitable for political parties / organisations that deal with memberships:

- The management of SEPA mandates (direct debit - automatic withdrawal)
- Direct debit refusals
- The reporting on membership payments (retrocessions / membership breakdown)

## Creation of SEPA mandates 

In Mozaik, memberships can be paid with a bank mandate (direct debit). Members will create a SEPA bank mandate by providing their account number and the organisation will be allowed to "collect" the money on the member's account every year when the membership is renewed. SEPA files can easily be generated in Odoo (with all your memberships) and uploaded on your bank website to proceed to the automatic withdrawals. This is saving time for the organisation and increases the members retention, as their membership is automatically paid every year.

!!! info 

    With SEPA Direct Debit, an organisation can collect money in any country in the SEPA area, as long as a valid bank mandate is proposed to the bank. 

<figure markdown>
![screenshot 24](img/screen24.png)
<figcaption>Example of a SEPA mandate</figcaption>
</figure>

## Direct debit refusals

When direct debits (automatic withdrawals) don't succeed (refusal by the member, insufficient funds etc ...), a direct debit refusal document will be issued by the bank. This refusal can be uploaded in Mozaik in order to:

- Mark the current membership as unpaid
- Cancel the existing direct debit SEPA mandate
- Send an automatic email to the member to indicate that the membership is still open and ask him to
    - pay the membership online (with Paypal, Sips or any other payment acquirer proposed by Odoo)
    - pay by bank transfer
    - create a new bank mandate

<figure markdown>
![screenshot 25](img/screen25.png)
<figcaption>Example of a membership line with the payment link</figcaption>
</figure>

## Reporting on membership payments

Some organizations with subscriptions send a portion of the subscription proceeds back to local chapters (based on each member's zip code) to support them and help them organise activities / find new members etc...
Some reporting tools in Mozaik help organisations and political parties to calculate the amount of those retrocessions / membership breakdowns.