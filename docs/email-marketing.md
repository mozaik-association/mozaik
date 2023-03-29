# Marketing emails

As the standard Odoo module that allows to create mailing lists, the Mozaik module - wich is more powerfull and complete than the Odoo standard - provide you to manage the marketing emails of the organisation.

It will provide access to :

- The general information of the marketing emails
- The recurrent mailings
- The management of failures
- The reporting

## General information

This functionality allows you to create, modify and manage all the emails marketing of your organisation.

The emails marketing provides access to general information:

- The general information of the emails marketing (subject, preview text, recipients...).
- The inclusion of opt-out contacts or not.
- The use of the mail template or not. 

!!! abstract "The goal of email management"

    This feature allows you to :
    
    - Create an email with a subject and a preview text.
    - Include contacts even if they have an op-out communication preference.
    - Choose to create an email from an Odoo template or to write a mail with the simplified mail editor. For the simplified mail editor, you also have the possibility to create mail templates in advance and simply select the one you need when creating a mailing. Thereafter, with the Odoo standard, you have the possibility to customize the content of the mail by adding personalized fields as the name or address of each recipient.

!!! info 

    A "global opt-out" box can be checked on a member's form to be blacklisted from receiving mass communications from the organisation. However, the contact will still receive the usual emails

<figure markdown>
![screenshot 19](img/screen19.png)
 <figcaption>Marketing email form with general information</figcaption>
</figure>

## Recurrent mailings

In the mailing configurations, it is possible to select the "recurrent sending" option by selecting the date of the next mailing and the time interval between mailings.

!!! abstract "The goal of recurrent mailing"

    This fonctionnnality allows you to send a mailing evey X hour/day/week/month/year. 
    
    Thanks to the distribution lists module and to this functionality, you can send a recurring email to a specific distribution list that is constantly updated thanks to dynamic filters.
    !!!example 

        I want to send automatically an email to all the people who participated in an event in the last three days. 

        To do this you will have to create a distribution list that includes, thanks to the filters, the people who participated in an event in the last three days. The filters being dynamic, the distribution list will be constantly updated. Once the list is created, in the mailing configuration you will have to select a recurrent mailing every 3 days.

<figure markdown>
![screenshot 20](img/screen20.png)
 <figcaption>Example of recurrent mailing</figcaption>
</figure>  

## Management of failures

All communication failures must be recorded in the application. This information is visible on the record of each contact in the "communication" tab. If a contact does not receive an email or a letter sent, a communication failure will be recorded on his contact's form.
!!! abstract "The goal of failure management"

    This fonctionnnality allows you to blacklist a contact after a certain number of failure to stop sending him emails or letters that he will not receive.

How to encode failures on the  contact's form ? :

- Postal returns: must be manually encoded 
- Electronic returns: records are automatic

<figure markdown>
![screenshot 23](img/screen23.png)
 <figcaption>Example of encoded failures</figcaption>
</figure>  

## Reporting

The module offers :

- A reporting tab to get a global analysis of the different mails with several measures over the time (number of sendings, returns, openings...).
- An individual report for each mail sent with different information such as the opening rate, the click rate, the return rate ....

<figure markdown>
![screenshot 26](img/screen26.png)
 <figcaption>Example of individual report</figcaption>
</figure>  