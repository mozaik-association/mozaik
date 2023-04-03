# Distribution lists

The Mozaik distribution list module offers additional functionalities to complement the Odoo standard. The module provides you to manage distribution lists of your organisation.
It will provide access to :

- The general information of the distribution lists
- The inclusion and exclusion filters
- The export

## Distribution list

This functionality allows you to create, modify and manage the distribution lists related to your organisation.

The distribution list module provides access to general information:

- The general information of the distribution list (name, note...).
- The list of contacts included in the distribution list.

!!! abstract "The goald of the distibution list" 

    You can create a distribution list by giving a name to this list. The distribution list will create a list of specific contacts based on filters you created. It will be used to target specific targets based on the following criteria and then send emails to these targets using the <a href=https://mozaik-association.github.io/mozaik/email-marketing tagret="_blank">marketing email module</a>. 

<figure markdown>
![screenshot 51](img/screen51.png)
 <figcaption>Distribution list form with general information</figcaption>
</figure>


## Include and exclude filters

    
A distribution list allows you to add filters that allow you to find a list of contacts that meet these filters and that will be included or excluded of the distribution list. Filters can be created and saved as a template to be used for other distribution lists.

As with the include filters, the exclude filters work in the same way. Simply create one or more new filters that can be saved as a template to be reused later. Once the filters are selected, you can display a list of all the contacts that will NOT be part of the distribution list.

Several filters can be added to a distribution list in order to refine the list of contacts
 as much as possible.

!!!info

    These filters are dynamic, when a new person meets the criterias of the filters, this person will be automatically added in the distribution list.
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

??? tip

    You can access to this fonctionnality by clikcing on the "mass action" button in a distribution list form below the "edit" button