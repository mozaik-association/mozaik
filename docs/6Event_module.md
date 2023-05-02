# Events

The Mozaik events module uses the Odoo standard and adds specific features for political parties and other organisations. It allows you to manage the different events of your organisation.

The Mozaik Events module differs from the Odoo standard module by several points :

- The management of interests and categories of participation linked to the questions asked to the participants in order to collect information on the contacts participating in the events.
- The management of the voting domain in order to allow certain people to participate in votes or not during the event.
- The event access management, in order to limit access to certain people according to their access rules (< local instance)

## General information of the events


This functionality allows you to create, modify and manage the events related to your organisation.

Various information can be completed on a event form :

- The standard information of the event (name, dates, organizer...)
- The interests related to the event.
- The involvement categories related to the event.

The interests and involvement categories linked to the events allow the organisations to find all the contacts with certain categories of participation or interests in order to send communications in a verry targeted manner.

!!! abstract "The goal of event management"

    This functionality allows to :

    - Manage the general information of each event.
    - Add tags/interests to categorise the different events and add these interests to the form of the contacts who attended to this event.
    - Add involvement categories to automatically add them to the form of the contacts who participated to the event.
    - Get access to the lists of all the attendees and sponsors of each event.

<figure markdown>
![screenshot 40](img/screen40.png)
<figcaption>Event form with general information</figcaption>
</figure>

## Questions

The module allows you to add questions in the "questions" tab that participants can or must answer. Answers can be free text, multiple choice or a tickbox.

!!! abstract "The goal of the questions"

    Thanks to Mozaik, the answers to the questions asked to the participants of the events can be linked to categories of participation and centres of interest also called thesaurus therms in Mozaik. This feature allows to collect information on the participants according to their answers to the questions. This information will later be displayed on the contact's form of the participants. This information can be reused afterwards to send mailings to your contacts in a very targeted manner.
    !!! example 

        People answering "yes" to the question "Would you like to stay informed about the other events about pensions?" will receive a category of participation and an interest in this subject.
        <figure markdown>
        ![screenshot 43](img/screen43.png)
        <figcaption>Adding a participation category and an interest based on the response</figcaption>
        </figure>

<figure markdown>
![screenshot 44](img/screen44.png)
<figcaption>Example of questions</figcaption>
</figure>

## The voting domain

A voting domain can be registered in the "voting domain" tab on an event, to indicate which members are allowed to vote during an event. This information will be displayed when the barcode on the badge of the participant is scanned / when the participant's name is encoded in the system.

!!! example 

        I only want to allow people who are members since more than 5 years to vote.
        <figure markdown>
        ![screenshot 45](img/screen45.png)
        <figcaption>Example of a voting domain</figcaption>
        </figure>

## The access limitations

Thanks to the "security" tab, it is possible to limit the visibility and access of each event to certain people depending on their access rights.
This access rules are based on the internal structure of the organization. A user linked to a very low internal intance will only be able to access the events linked to his instance. A user linked to the 'regional' internal instance will be able to access all the events of his region etc.

!!! example 

    I want that only people from the Antwerp instance can access to the event.

<figure markdown>
![screenshot 46](img/screen46.png)
<figcaption>Example of an access limitation</figcaption>
</figure>