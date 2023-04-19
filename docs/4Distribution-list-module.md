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

    Distribution lists are used to create lists of contacts that meet specific criteria defined by filters created beforehand. These distribution lists can then be selected when creating marketing emails to target specific contacts using the <a href=https://mozaik-association.github.io/mozaik/email-marketing tagret="_blank">marketing email module</a>. 

<figure markdown>
![screenshot 51](img/screen51.png)
 <figcaption>Distribution list form with general information</figcaption>
</figure>


## Include and exclude filters (A REFORMULER POUR QUE CE SOIT PLUS PROPRE EN ANGLAIS ET QU'ON COMPRENNE BIEN, BIEN EXPLIQUER COMMENT LES FILTRES SONT CREES CAR ON PART TOUJOURS DES MODELES VIRTUELS QUI RENDENT CELA PLUS SIMPLE + dire qu'on peut mettre des filtres issus de différents modèles (aussi bien des mandats que des adhésions. Un filtre est déjà un ensemble de filtres. Renvoie le fonctionnement des listes de distribution dans Odoo stp pour bien comprendre cette partie))

    
A distribution list allows you to add filters that allow you to find a list of contacts that meet these filters and that will be included or excluded of the distribution list. Filters can be created and saved as a template to be used for other distribution lists.

As with the include filters, the exclude filters work in the same way. Simply create one or more new filters that can be saved as a template to be reused later. Once the filters are selected, you can display a list of all the contacts that will NOT be part of the distribution list.

Several filters can be added to a distribution list in order to refine the list of contacts as much as possible.

!!!info

    These filters are dynamic, In case one or more new contacts meet the criteria of a filter, these new contacts will automatically be added to the distribution list. 
    !!!example

        You want to create a filter that includes all contacts in good standing who have a voluntary participation.

        The filter will constantly update the list of relevant contacts, including those in good standing who have a voluntary participation and will not take over the others.

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