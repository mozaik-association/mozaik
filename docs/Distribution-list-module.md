# Distribution list module

As with the standard Odoo module that allows to create mailing lists, the Mozaik distribution list module provide you to create distribution lists. Its advantage compared to the standard Odoo module is that it is much more complete and powerful.

This module will give you the opportunity to:

- Create distribution lists
- Create inclusion and exclusion filters
- Export information

## Distribution list
You can create a distribution list by giving a name to this list. The distribution list will create a list of specific contacts based on filters you created and will be used to target specific targets based on the following criteria and then send emails to these targets using the <a href=https://mozaik-association.github.io/mozaik/email-marketing tagret="_blank">the marketing email module</a>. 


## Include and exclude filters

    
A distribution list allows you to add filters that allow you to find a list of contacts that meet these filters and that will be included or exclude of the distribution list. Filters can be created and saved as a template to be used for other distribution lists. Once the different filters are added, it is possible to see the list of all the contacts found by applying the different filters. 

As with the include filters, the exclude filters work in the same way. Simply create one or more new filters that can be saved as a template to be reused later. Once the filters are selected, you can display a list of all the contacts that will NOT be part of the distribution list.

:warning: To be included in these lists, it is mandatory that the contact has at least one email or postal address defined. Otherwise, the contact will appear in the "Without coordinate" tab accessible from the mailing list form.

!!!info

    These filters are dynamic, when a new person meets the criteria of the filters, this person will be automatically added in the distribution list.
    !!!example

        You want to create a filter that includes all contacts in good standing who have voluntary participation.

        The filter will constantly update the list of relevant contacts, including those in good standing who have voluntary participation and will not take over the others.

??? tip

    By clicking on the "list result" button at the top right of the form, you can access the list of contacts that are part of the distribution list once the filters are active.

<figure markdown>
![screenshot 18](img/screen18.png)
 <figcaption>Creation of a filter</figcaption>
</figure>

## Exporting

The module provides users with a tool that allows them to export a whole series of information from the contacts in the distribution list. This tool can generate a structured file (CSV) for an external printing tool (printing of membership cards).

![screenshot 22](img/screen22.png)

??? tip

    You can access to this fonctionnality by clikcing on the "mass fonctionality" button in a distribution list form.