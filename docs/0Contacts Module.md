# Contacts Fact

The contact module - which is a central module in Mozaik - allows to manage the contacts related to your organisation / political party.  It will give you access to:

- The general information about each contact (members, supporters, all other contacts)
- The interests & competencies of each contact
- The participations of each member (interactions with the organisation)
- The management of duplicates and co-residencies
- <a href="https://mozaik-association.github.io/mozaik/1Memberships/" target="_blank">The Membership details</a>.

## Contacts: People management (individuals & companies)

This functionality allows you to create, modify and manage the contacts (members/subscribers/other contacts) related to your organisation.

Various informations can be collected for each contact (individuals or companies): 

- The standard information of a contact : name, first name, phone, address...
- Some personal information: age, gender, disability, social networks... 

!!! info "Address"

    The encoding of addresses on the contact form is facilitated by the auto-completion functionality that the system provides. This functionality allows you to choose the city and the street from a list of predefined choices. It is use to avoid encoding errors and helps detect duplicates. 

    :warning:Depending on their address, the contacts are associated with a local group/instance of the organisation. When the address changes, the instance of the contact can also be updated.
    !!! example
    
        A contact whose address is located in Brussels will belong to the Brussels local group of the organisation. If a member moves from Brussels to Antwerp, this member will now be related to the local group linked to the city of Antwerp.

!!! abstract "The goal of people management"

    This feature allows you : 

    - To manage the information about your contacts.
    - To get to know your members and supporters better.
    - To use personal information of your members for membership purposes (membership fee).

<figure markdown>
  ![screenshot 27](img/screen27.png)
  <figcaption>Contact form with general & personal information </figcaption>
</figure>

<figure markdown>
![screenshot 1](img/screen1.png)
<figcaption>Creation of an address with the auto-completion function</figcaption>
</figure>

## Indexation

Contacts (members, supporters, other contacts) can be linked to interests and competencies. Those interests and competencies are chosen from a list of terms, called Thesaurus terms in Mozaik and can be adapted according to the needs of each organisation.

!!! abstract "The goal of Thesaurus terms" 
    
    Those interests and competencies are present for information purposes (to better know your members and supporters), but also to achieve specific targeting with the communication tools / mass mailings.
    !!! example

        I would like to send a newsletter around 'Nuclear energy' to members who are interested by this topic. 
        
        More informations about how to target contacts based on those informations in the chapter about the <a href="https://mozaik-association.github.io/mozaik/Distribution-list-module/" target="_blank">distribution list module</a>.

Interests and competencies can:

- Be added manually by contacts during their registration.

!!! example

    I am interested by the themes of 'nuclear energy' and 'human right'

- Automatically when a member registers for a specific event / survey or petition 

!!!example

    If the petition that is signed by a member concerns 'nuclear energy', the related 'Thesaurus term' can automatically be added as 'Interest' for this member.

<figure markdown>
![screenshot 7](img/screen7.png)
<figcaption>Example of a contact form with Thesaurus terms</figcaption>
</figure>

## Involvements

This functionality enables you to add all the interactions between your organisation and its members / supporters. The types of interactions can be defined by each organisation according to their needs (signature of a petition, participation to a volontary action...)

!!!abstract "Goal of the involvements"

    Involvements allow you to get to know your contacts better / categorize them / keep a record of interactions with a particular contact over the years. These entries can be used to send mailings to your contacts in a very targeted manner.
    !!!example
        A member made a donation on 31/03/2023 and signed a petition about disarmement one week later. These participations will appear on his contact form and can be used in future mailings (send an email to all donors who have signed a petition in the last 2 months)
How to add them :

- An involvement can be added manually on a contact page.
- An involvement can be added automatically through a membership form.
- An involvement can be added automatically through the signature of a petition, the completion of a survey or the participation to an event.



<figure markdown>
![screenshot 28](img/screen28.png)
<figcaption>Example of a contact form with participations</figcaption>
</figure>

## Duplicates

A very elaborated duplicate check system has been implemented. It is based on :

- Name
- Phone
- Mobile
- Email 
- Address

It helps you identify, manage and merge possible duplicates within your contacts database. 

!!! info

    When a duplicate is detected, a button “show all duplicates” appears on the contact form of the duplicate members. This button provides you to display the list of contacts with one or more identical fields.
    <figure markdown>
    ![screenshot 2](img/screen2.png)
    <figcaption>Appearance of the button "Show all duplicates"</figcaption>
    </figure>


## Co-residencies

When two or more people share the same address, they can be grouped into a co-residency. This idicates that those people are no duplicates but simply live in the same accomodation.

Co-residencies allow you to :

- Avoid duplicates within your contacts database.
- Link people from the same family to each other.
- Avoid sending 2 letters to the same address.

??? question "How to create a co-residency ?" 

    You can create a co-residency by selecting your contacts, clicking on "action"--> "create a co-residency address” and entering the name of the co-residents in "line 1 and 2" 
    <figure markdown>        
    ![screenshot 3](img/screen3.png)
    <figcaption>Creation of a co-residency</figcaption>
    </figure>

!!! info

    Once you have created a co-residency or allowed the duplicates, the "show all duplicates" button will disappear.

<figure markdown>
![screenshot 33](img/screen33.png)
<figcaption>Example of a contact with a co-residency</figcaption>
</figure>