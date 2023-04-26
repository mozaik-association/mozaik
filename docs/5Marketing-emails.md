# Email marketing
The 'Email marketing' module offers additional functionalities to complement the Odoo standard module. The module enables users to manage the marketing emails of their organisation.

REECRIRE ICI POUR NE METTRE QUE CE QUI CHANGE PAR RAPPORT AU STANDARD. IL N'EST PAS IMPORTANT DE PRECISER ICI LES INFOS GENERALES DU MODULE SI C'EST LA MEME CHOSE QUE LE STANDARD (il faut donc juste parler de la checkbox 'include opt out', de la possibilité de travailler avec des listes de distribution(en plus des listes de diffusion standards d'Odoo) et de la possibilité de travailler avec des modèles mail depuis là aussi (et pas le generateur standard Odoo))

It will provide access to:

- The general information of your marketing emails
- The recurrent mailings
- The management of failures
- The reporting

## General information

This functionality allows you to create, modify and manage the emails marketing sent by your organisation.

The emails marketing provides access to general information as:

- The general information of the emails marketing (subject, preview text, recipients...).
- The inclusion of opt-out contacts or not.
- The use of the mail template or not. 

!!! abstract "The goal of email management"

    This feature allows you :
    
    - To create an email with the general informations needed as the subject and a preview text.
    - To include contacts even if they have an op-out communication preference on their contact's form.
    - To choose to create an email from the Odoo template or to write a mail with the simplified mail editor of Mozaik. The simplified mail editor allows you also to create mail templates in advance and simply select the one you need when creating a mailing.

!!! info 

    A "global opt-out" box can be checked on a member's form to be blacklisted from receiving mass communications from the organisation. However, the contact will still receive the usual emails

<figure markdown>
![screenshot 19](img/screen19.png)
 <figcaption>Marketing email form with general information</figcaption>
</figure>

## Recurrent mailings

In the mailing configurations, it is possible to select the "recurrent sending" option by selecting the date of the next mailing and the time interval between mailings.



!!! abstract "The goal of recurrent mailing"

    This functionality allows you to send automatically an email evey X hour/day/week/month/year. 

    IL MANQUE DES MOTS AU DEBUT DE TA PROCHAINE PHRASE. IL FAUT PRECISER ICI QUE LES MAILS NE SONT ENVOYES QU'UNE SEULE FOIS A CHAQUE CONTACT ET QUE L'IDEE EST DONC D'INCLURE LES PROCHAINS QUI CORRESPONDENT A CES CRITERES DANS LE FUTUR. ODOO VERIFIE S'IL Y A DES NOUVELLES PERSONNES QUI CORRESPONDENT AU DOMAINE LORS DE CHAQUE ENVOI.
    
    added to the distribution list module, the email marketing module allows you to send a recurring email to a specific distribution list that is constantly updated thanks to the dynamic filters.
    !!!example 

    METTRE UN MEILLEUR EXEMPLE SUR LES ADHESIONS PAR EXEMPLE (TOUS CEUX QUI ONT PAYE LEUR ADHESION DANS LES DERNIERES HEURES POUR LES REMERCIER. ET DEUXIEME EXEMPLE: TOUS CEUX QUI ONT PLUS DE 30 ANS ET QUI ONT SIGNE UNE PETITION DANS LES 24 DERNIERES HEURES)

        I want to send automatically an email to all the people who participated in an event in the last three days. 

        To do this you will have to create a distribution list that includes, thanks to the filters, the people who participated in an event in the last three days. The filters being dynamic, the distribution list will be constantly updated. Once the list is created, in the mailing configuration you will have to select a recurrent mailing every 3 days. Every 3 days only new people who have participated in an event will receive the email.

<figure markdown>
![screenshot 20](img/screen20.png)
 <figcaption>Example of recurrent mailing</figcaption>
</figure>  

## Management of failures

All communication failures (email / postal) can be recorded in the application. This information is visible on the contact's form of each contact, in the "communication" tab. If a contact does not receive an email (bounce) or a letter, a communication failure can be recorded on his contact's form.

!!! abstract "The goal of failure management"

    This functionality allows you to register the communication failures of each contact. Thanks to this functionality, you can automatically blacklist a contact after a certain number of failures to stop sending him emails or letters that he will not receive.

How to encode failures on a contact? 

- Postal bounces: must be encoded manually
- Email bounces: records are updates automatically by Mozaik

<figure markdown>
![screenshot 23](img/screen23.png)
 <figcaption>Example of encoded failures</figcaption>
</figure>  

RAJOUTER UN EMAIL BOUNCE DESCRIPTION (VA VOIR DES EXEMPLES SUR INTERNET POUR TROUVER QQCHOSE D'INTERESSANT)

## Reporting

The module offers :

- A reporting tab to get a global analysis of the different mails with several measures over the time (number of sendings, returns, openings...).
- An individual report for each mail sent with different information such as the opening rate, the click rate, the return rate ....

<figure markdown>
![screenshot 26](img/screen26.png)
 <figcaption>Example of an individual report</figcaption>
</figure>  