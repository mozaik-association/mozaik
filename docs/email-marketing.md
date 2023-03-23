# Marketing emails

As with the standard Odoo module that allows to create mailing lists, the Mozaik module - wich is more powerfull and complete than the Odoo standard - provide you to manage the marketing emails of the organisation.

It will provide access to :

- The general information of the distribution list
- The recurrent sending
- The follow-up of the different emails in progress
- Management of failures
- Reporting

## General information

This functionality allows you to create, modify and manage all the emails marekting.

The demails marekting provides access to general information:

- The general informations of the email marketing (subject, preview text, recipients...).
- The inclusion of opt-out contacts or not.
- The use of the mail template or not. 

!!! abstract "The goal of email management"

    This feature allows you to :
    
    - Create an email with a subject and a preview text.
    - Include contacts even if they have an op-out communication preference.
    - Choose to create an email from an Odoo template or to write a mail with a simplified mail editor. For the simplified mail editor, you also have the possibility to create mail templates in advance and simply select the one you need when creating a mailing. Thereafter, with the Odoo standard, you have the possibility to customize the content of the mail by adding personalized fields as the name or address of each recipient.

!!! info 

    A "global opt-out" box can be checked on a member's form to be blacklisted from receiving mass communications from the organisation. However, the contact will still receive the usual emails

<figure markdown>
![screenshot 19](img/screen19.png)
 <figcaption>Marketing email form with general information</figcaption>
</figure>

## Recurrent sending

In the mailing configurations, it is possible to select the option "recurrent sending" by selecting the date of the next mailing and the time interval between mailings  

!!! abstract "The goal of recorrent mailing"

    This fonctionnnality allows you to send a mailing evey X hour/day/week/month. Thanks to the filters of the distribution lists module and to this functionality, you can send a recurring email to a specific distribution list that is constantly updated thanks to dynamic filters.
    !!!example 

        I want to send automatically an email to all the people who participated in an event in the last three days. 

        To do this you will have to create a distribution list that includes, thanks to the filters, the people who participated in an event in the last three days. The filters being dynamic, the distribution list will be constantly updated. Once the list is created, in the mailing configuration you will have to select a recurrent mailing every 3 days.

<figure markdown>
![screenshot 20](img/screen20.png)
 <figcaption>Example of recurrent mailing</figcaption>
</figure>  

## Follow-up of the mails

The marketing email module allow you to folluw-up the stage of your differents emails in progress. The differents items are displayed in a kanban view and automatically move from one stage to another depending on whether they are still in project, pending, being sent or sent. 

## Management of failure

All communication failures must be recorded in the application. This information is visible on the record of each contact. If a contact does not receive an email sent, a communication failure will be recorded on his card.
!!! info inline end "Info"

    After a certain number of errors, the contact can be placed in a blacklist in order to not continue to send him emails that he will not receive.

- Postal returns: must be manually encoded 
- Electronic returns: records are automatic
- Unsuccessful phone calls: must be manually entered 

![screenshot 23](img/screen23.png)

## Reporting

The email marketing module offers analysis of different mailings over time. It is also possible to see the details of different information such as the opening rate or the click rate of each mailing.

![screenshot 26](img/screen26.png)