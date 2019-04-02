# DoES Liverpool Software Infrastructure

We use a collection of services and pieces of software - some off-the-shelf, others developed in-house - to help with the smooth running of the space/community.

## Promotional/Comms

 * Google Group - main online discussion group (used as a mailing list)
 * Mailchimp - announcements list
 * Twitter - @doesliverpool
 * Instagram - @doesliverpool
 * Slack - more immediate chat group
 * Facebook 
 * Weeknote-generator script runs once-a-week to create a blog post

## Informational

 * The main [doesliverpool.com](http://doesliverpool.com) website.  Built on Wordpress.  Main public-facing website.
 * [Main wiki](https://github.com/DoESLiverpool/wiki/wiki).  Holds the non-sensitive information about the space and community, processes, equipment, etc.
 * Restricted-access wiki.  The place where account details and other sensitive information is held, accessible to organisers and directors.
 * [status.doesliverpool.com](http://status.doesliverpool.com) tracks the status of a variety of DoES Liverpool services and equipment, mostly automatically from the "Broken" label in the Somebody Should issue list.

## Financial

 * FreeAgent is used to manage the accounts
 * PayPal for additional payments
 * iZettle for credit card payments

## Administrative

 * Google spreadsheet to track people's visits and predict cashflow
 * Doorbot code contains the nearest we have to a member database, and controls access to the different rooms in the space
 * Somebody Should issue list tracks to-do items
 * SupportBee as a help-desk back-end to ease distribution of handling email enquiries to hello@doesliverpool.com
 * Google calendars to manage:
   * bookings for the laser-cutters
   * inductions on the laser-cutters
   * bookings for meetings in Dinky
   * booking hot-desks
   * availability of organisers to open/close the space each day
   * events/meetups happening at the space
 * YouCanBookMe to provide an easier booking system for members to book the laser-cutters, an induction, hot-desks, meetings in Dinky

# Types of User

Who interacts with DoES Liverpool, and in what sort of way?  These roles aren't always exclusive - i.e. one person could be a maintenance team member at one point, and a member booking a desk at another time...

 * Member of the public.  Doesn't know anything (or much) about DoES Liverpool, is encountering us for the first time
 * Event attendee
 * Event organiser
 * Casual user.  Hot-desks from time to time, or books the laser every now and then when they need it
 * Regular user
 * User with out-of-hours access
 * Member
 * Maintainer.  Someone who is fixing or performing routine maintenance on a piece of equipment or on the space in general
 * Organiser.  Someone who answers the door and/or the phone, and potentially email discussions
 * Maintenance team member
 * Grievance team member
 * Administrator
 * Director

# Improvements

There's a slow project under way to consolidate/improve some of the systems.  Not everything must be integrated into a seamless all-singing-and-dancing app, in fact, the principle of small pieces, loosely joined is more appealing.  However, better joining of the systems to ease the administrative overhead would be good, so the first step is identifying what should be replaced and what new connecting code should be developed.

The following Somebody Should issues are related to this (and provide additional background):
 * [We need a system for managing hot desk use #45](https://github.com/DoESLiverpool/somebody-should/issues/45)
 * [User Management #175](https://github.com/DoESLiverpool/somebody-should/issues/175)
 * [There should be a better way of adding people to the doorbots #166](https://github.com/DoESLiverpool/somebody-should/issues/166)
 * [Review and improve our administrative software usage #670](https://github.com/DoESLiverpool/somebody-should/issues/670)
 * (this isn't intended to be an exhaustive list, just to provide some useful jumping off points for more info)
 
# Use Cases
 
In rough order, from **must have** to **nice to have**...

 * As an organiser, I want to be able to predict cashflow.
     * FabManager provides statistics, possibly not this exactly but there's a way to do it.
 * As an organiser, I need to know how much money we make from event room rentals.
     * FabManager -> Statistics -> Events
 * As an organiser, I want a single source of truth for what membership level/access level a member has.
     * FabManager -> Users -> Find user
 * As an organiser, I want to know which members have completed an induction.
     * FabManager -> Users -> Edit user -> Trainings
     * FabManager -> Statistics -> Trainings
 * As an organiser, I want to make sure that out of hours members have completed the opening/closing induction.
     * FabManager -> Users -> Edit user -> Trainings
 * As an organiser, I want to track who has a free 'cake day' so that people can't have multiple free days!
     * FabManager -I wondered if this could be done as a subscription, but it seems you can only have one subscription at a time.
 * As an organiser, I want to make sure that out-of-hours members have paid a deposit.
     * FabManager - ould it go in as a Training
 * As an organiser, I want to make sure people get invoiced for the services they use - automatically if possible!
     * FabManager - Subscriptions seem to cover this but you can only have one and I'm not sure if the payment will recur automatically.
 * As a user, I want to be able to book a hotdesk.
     * FabManager - Can create a recurring daily event that people can book for, essentially covers this although isn't the nicest interface.
 * As a user, I want to be able to book a room for a meeting or event.
     * FabManager - If I create a room as a "Machine" then this works (and the hour slots work ok here). Can't recur slots, would need a script.
 * As a user, I want to be able to book a laser-induction.
     * FabManager - Yes, can do this. Can't recur the training slots though, would need a script to do this.
 * As a user, I want to be able to book time on the CNC and laser machines.
     * FabManager - Yes, can do this. Can't recur slots, would need a script.
 * As a member of the public, I want to see which events are on at DoES.
     * FabManager - Yes, the calendar is a bit busy with all the hot desk events showing up
 * As a potential hotdesker, I want to be able to book a hotdesk without having to set up an account/password.
     * FabManager - Not possible, would need something extra
 * As a user, I want to see an itemised breakdown on my invoices so that I can check it always is correct.
     * FabManager - Invoices do appear to show a full breakdown
 * As a hotdesker, I want to know how many days I have left in this month's allocation.
     * FabManager - Doesn't appear to be a function they offer
 * As an organiser, I want people to be able to book rooms by the hour but machines by the half-day.
     * FabManager - Doesn't appear to be possible by default, can't find a way to change the size of the slots. When booking you can book multiple slots at once though.
 * As a user, I want clearer signposting/navigation between the various DoES systems and processes.
     * FabManager - No
 * As an organiser, I want doorbot access control to be managed more automatically so it matches members' payments/status.
     * FabManager - It seems like we could do this, possibly using labels too.
 * As a member *while in the space*, I want to know the names and access privileges of the other people currently in the space.
     * FabManager - It seems like we could do this as a report
 * As an organiser, I want to be able to track usage of paid-for materials/consumables.
     * FabManager - Not seeing anything for this
 * As a user, I want a single site to manage all my interactions with DoES.
     * FabManager - That's the aim, not sure it covers everything yet
 * As someone helping with a DoES project or event, I want to know how much money (expenses) have been spent on the project/event so I can manage my budget.
     * FabManager - No
 * As a user, I want it to be very easy to report issues with the space/equipment.
     * FabManager - Not through fab manager
 * As a 1st time/potential user, I want to get a better sense of what DoES is about, so I can decide whether to visit the space.
     * FabManager - Not really, although it does have projects
 * As an organiser, I want to be able to see the counts of desk, workshop, hot-desk usage over time so that I can look for trends in membership when doing longer-term planning
     * FabManager - There are some statistics
 * As a user, I want to need as few user accounts as possible to interact with doES processes.
     * FabManager - This could help
 * As an organiser, I want a way to manage enquiries from social media users.
     * FabManager - Not really
 * As an organiser, I want a system to manage email enquiries to hello@doesliverpoool.com as part of a team.
     * FabManager - Not really
 * As a user, I want to be able to pre-book to hot desk or use a machine and pay by cash when I arrive
     * FabManager - Doesn't appear to be an option
