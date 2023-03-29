# Mandates
The mandate module allows you to manage all the mandates related to your organisation. Different categories of mandates are possible:

- The states mandates
- The internal mandates 
- The external mandates

These three types of mandates are managed in a similar way. Only the data changes.

Each gategory of mandate give you access to :

- The selection comittee
- The statuts of the mandates
- The invalidation of mandates
- The renewal of mandates

## Selection committee

In order to select a person for a term of office, the first step is to create a selection committee. It is created with the information previously created in the Mozaik structure module (Legislature, designation assembly...).

Once the selection committee is created, you can add a candidate to this committee by choosing the candidate on the new candidate form.

!!!info

    This whole part is an option offered by Mozaik to better follow-up the election of proxies. However, it is possible to directly create a mandate without going through these steps.

<figure markdown>
![screenshot 15](img/screen15.png)
 <figcaption>Creation of a committee</figcaption>
</figure>

<figure markdown>
![screenshot 16](img/screen16.png)
 <figcaption>Adding new candidates</figcaption>
</figure>


## Status of the canddiates

Once a new canddiate is declared, he must be nominated then elected to create a new mandate. 

``` mermaid
graph LR
  A[Declared status] --> B[Rejected];
  A --> C[Nominated];
  C --> D[Not elected];
  C --> E[Elected];
```

<figure markdown>
![screenshot 57](img/screen57.png)
 <figcaption>Management of the status of the candidates</figcaption>
</figure>

## Invalidation of mandates

The mandates are characterized by three dates: beginning of mandates, end date and expiration date. It is possible to invalidate the mandate, end it:

- Automatically on the expiry date.
- Manually by setting an end date before the expiration date.

## Renewal of mandates
The module allows you to renew a mandate by clicking on the "renew" button in the "State Mandates" tab.

!!! abstract "The goal of this fonctionnnality"

    - This fonctionnnality allows you to renew a mandate automatically without going through the election phase.
    - This fonctionnality allows you to create a second mandate for the same person, for the same assembly, at the same period but for another position.
    !!!example

        I want to create a mandate of sénator in addition of a mandate of minister for the same persoon. 

![screenshot 17](img/screen17.png)

??? tip

    It is possible to create and retrieve all categories of mandates for political mandates - internal and external by clicking on "configurations" then "categories of mandates"

## Retrocessions
