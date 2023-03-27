# Invoices

The Mozaik invoicing module includes most of the features of the standard Odoo module. This module is designed to simplify invoicing in order to get paid faster. It allows you to :

- Automatically invoice based on purchase orders
- Delivery orders, contracts
- Generated expense sheets
- Accept online payments.
- Eliminate the hassle of reminders for late payments.
- Simplify the configuration of automatic follow-up.
- Keep track of bank account movements and invoice status.

Mozaik does however offer some additional functionality suitable for organisations :

- Creation of SEPA mandates
- Management tool for direct debit refusals

## Creation of SEPA mandates 

When creating a membership, you will be asked to fill in a field with a bank account number. Once this bank account is completed and the membership created, a SEPA mandate is automatically created.

<figure markdown>
![screenshot 24](img/screen24.png)
<figcaption>Example of a SEPA mandate</figcaption>
</figure>

## Management tool for direct debit refusals

For the payment of memberships, it is possible to create a payment link that redirects to an Odoo payment page in order to make the payment with a payment intermediary compatible with Odoo.

![screenshot 25](img/screen25.png)

In the case where, for an unknown reason, a contact is refused his annual collection, a refusal management tool is activated. 

- An email is sent to the contact asking him to pay his membership since it has not been paid
- The direct debit is stopped (the mandate is cancelled) 
- A new membership line is opened

