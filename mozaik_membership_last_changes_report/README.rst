=====================================
Mozaik Membership Last Changes Report
=====================================

This module collects all important changes applied to specific partners, and allows to send a summary email (via a cron)
to the recipients of assemblies.

The changes can be consulted on the membership lines. They are erased as soon as the notification email is sent to the recipients (see below on how the recipients are chosen).

Configuration
-------------
A lot of changes can be notified. For each of these changes, the notification can be turned on or off. For eg. you have the following notifications:

* Log when partner joins an instance
* Log when partner becomes a supporter
* Log voluntaries changes
* Log email changes
* etc

You can also associate a sequence code for each of these changes, to order them.

Please configure this into General Settings > Membership

Emails are set to partners that have an internal mandate that is linked to an internal instance in which some partner had changes logged.
The email is only sent to partners whose internal mandate is in a category having the checkbox "Summary Mails Recipient" ticked.
