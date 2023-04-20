# Distribution lists

The Mozaik distribution list module offers additional functionalities to complement the Odoo standard 'diffusion lists' from the Email marketing module. 
This module enables to create lists of contacts that meet very specific and detailed criteria. To build this domain, you can:

- Use dynamic filters
- Build time-related filters
- Define multi-model domains
- Include / Exclude specific people (opt in / opt out) from distribution lists 

## Distribution lists

REECRIRE CETTE PARTIE POUR QUE CE SOIT PLUS INTERESSANT / DONNE PLUS D'INFOS SUR CE QUE SONT LES LISTES DE DISTRIBUTION OU CE QU'ON TROUVE DANS CE MENU (déjà evoquer ici les filtres inclus / exclus pour introduire la partie 2? ) 

This functionality allows you to create, modify and manage the distribution lists related to your organisation.

The distribution list module provides access to general information:

- The general information of the distribution list (name, note...).
- The list of contacts included in the distribution list.

!!! abstract "The goald of the distibution list" 

    Distribution lists are a powerful tool that can help you efficiently communicate with a targeted group of contacts. These lists are created based on a set of predetermined rules established by inclusion or exclusion filters that determine which contacts should be added or removed from the list.

    Once a distribution list has been created, it can be leveraged to target a specific group of contacts for mass communication. This can be especially helpful when using <a href=https://mozaik-association.github.io/mozaik/email-marketing tagret="_blank">marketing email module</a>, allowing you to send tailored messages to the right people.    
 

<figure markdown>
![screenshot 51](img/screen51.png)
 <figcaption>Distribution list form with general information</figcaption>
</figure>


## Include and exclude filters (A REFORMULER POUR QUE CE SOIT PLUS PROPRE EN ANGLAIS ET QU'ON COMPRENNE BIEN, BIEN EXPLIQUER COMMENT LES FILTRES SONT CREES CAR ON PART TOUJOURS DES MODELES VIRTUELS QUI RENDENT CELA PLUS SIMPLE + dire qu'on peut mettre des filtres issus de différents modèles (aussi bien des mandats que des adhésions. Un filtre est déjà un ensemble de filtres. Renvoie le fonctionnement des listes de distribution dans Odoo stp pour bien comprendre cette partie))

    
A distribution list enables you to apply filters that help you identify a group of contacts that meet specific criteria and can be added or removed from the list accordingly. You can create filters and save them as templates to use for other distribution lists.

Similar to the inclusion filters, exclusion filters work in the same manner. All you need to do is create one or more new filters that can be saved as a template for future use. Once the filters are applied, you can view a list of all the contacts that will be excluded from the distribution list.

Multiple filters can be use to fine-tune the list of contacts and ensure that only relevant individuals are included in the distribution list.

!!!info

    These filters are constantly changing, meaning that if there are new contacts that match the filter criteria, they will be automatically added to the distribution list.
    !!!example

        Suppose you want to create a filter that includes all contacts in good standing who voluntarily participate in a program. As more contacts meet these criteria, they will be added to the distribution list automatically without removing any of the existing contacts.

??? tip

    By clicking on the "result" button next to the filter you created, you can access the list of contacts that are part of the filters.

    :warning: To be included in these lists, it is mandatory that the contacts has at least one email or postal address defined. Otherwise, the contacts will appear in the "Without coordinate" tab accessible from the mailing list form.

<figure markdown>
![screenshot 18](img/screen18.png)
<figcaption>Creation of a filter</figcaption>
</figure>
<figure markdown>
![screenshot 56](img/screen56.png)
<figcaption>Distribution list form with a filter</figcaption>
</figure>

## The export

The module provides users with a tool that allows them to export a whole series of information from the contacts in the distribution list. This tool can generate a structured file (CSV) for an external printing tool (printing of membership cards).

<figure markdown>
![screenshot 22](img/screen22.png)
 <figcaption>Exporting of the distribution list</figcaption>
</figure>

??? question "How to use this functionality ?"

    You can access to this functionality by clikcing on the "mass action" button in a distribution list form below the "edit" button