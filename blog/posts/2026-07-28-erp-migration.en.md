---
title: The bugs that survive an ERP upgrade are the quiet ones
subtitle: Migrating five major versions forward across four companies and three countries
date: 2026-07-28
lang: en
slug: erp-migration
summary: Migrating five major versions forward across four companies and three countries. The failures that raised errors were fixed in days; the ones that changed behaviour without raising anything lasted weeks.
tags: odoo, migration, erp
---

The ERP I look after runs four operating companies in Chile, Colombia and Peru. It holds the inventory, the accounting, the purchase and sales orders, and the electronic invoicing that three different tax authorities require by law. When it stops, warehouses stop dispatching and invoices stop being issued — which, in countries where invoicing is a regulated act, is not an inconvenience but a compliance problem.

    
That system was five major versions behind. Moving it forward meant migrating the database, rewriting the custom code against a changed API, and re-certifying the electronic invoicing for three regulators — without losing a record and without a window long enough for anyone to notice.

    
The migration itself went well. What I want to write about is what came after, because that is where the real lesson was.

    
## The shape of the problem

    
The installation had around 228 modules, of which 41 were custom code written over several years by several hands. A good part of the work before touching anything was archaeology: reading every custom module to decide what was still load-bearing, what was dead, and what had quietly become a duplicate of something the platform now did natively. Forty-one custom modules became eighteen.

    
Consolidation was not tidiness for its own sake. Every custom module that overrides a standard model is a bet that the standard model will not change underneath it. Five versions is a lot of change. The fewer bets outstanding at cutover, the fewer ways the upgrade can surprise you.

    
The cutover ran on the platform's native upgrade path against a copy of production, then for real. The database identity was preserved, nothing was lost, and there was no rollback.

    
## Then the quiet failures started

    
I had prepared for the upgrade to break things loudly — a traceback, a module that refuses to load, an invoice that won't post. Those are the easy failures. They announce themselves, you fix them, you move on. Almost none of the real problems behaved that way.

    
The clearest example was a single field. In the old version, a line on an invoice that represented an actual product had an empty `display_type`; section headers and notes had a value. So code written across the system filtered product lines the obvious way: *take the lines where display_type is empty*. In the new version, product lines stopped being empty and started carrying an explicit value of their own.

    
Nothing errored. The filters still ran. They simply returned nothing, forever. Code that had worked for years kept executing, kept reporting success, and processed zero records.

    
That one change produced three separate bugs before I understood the pattern: a PDF that silently stopped compacting its lines, a consolidation routine for documents over the regulator's line limit that quietly stopped consolidating, and a ticket format that lost its content. Three symptoms, three areas, one cause — and not one of them raised an exception.

    
Once I recognised it, the fix was mechanical: audit *every* filter inherited from the old version that tested that field, and make it accept both shapes. The expensive part wasn't the fix. It was the weeks between the upgrade and the moment I knew to look.

    
## Four other ways it stayed quiet

    
The same pattern — no error, wrong behaviour — showed up in shapes I had not anticipated:

    
- **Scheduled jobs that outlived their code.** Job definitions from the old version survived the upgrade even when the method they called no longer existed. Every run failed silently. They were only visible by looking for jobs with a non-zero failure count — nothing surfaced them on its own.

      - **Stored computed fields that quietly desynchronised.** Some fields cache a value copied from somewhere else. The upgrade changed several of those sources without recomputing the copies, so the two disagreed. Everything looked normal until a report cross-referenced both.

      - **New platform behaviour colliding with old assumptions.** A standard nightly routine gained a new step that "repairs" inventory reservations. Our consignment warehouses deliberately violate the invariant that step enforces, for good reasons. The collision only ran at night, so the first symptom appeared more than twenty-four hours after the change that caused it — which is exactly long enough to stop suspecting the change.

      - **Code that was never running at all.** Two modules in our repository shared a name with modules the platform now ships. The platform's version wins. So a module I could read, edit and commit to had no effect whatsoever on the running system. Before fixing anything, verify that the file you are reading is the file being executed.

    
## The one that taught me the most

    
A new list view I added for one country became, without anyone touching it, the default list view for that record type across the entire system — in all four companies.

    
The reason is almost funny. Views are ordered by priority, then by name. My new view had the same priority as the standard one, and its name happened to sort earlier alphabetically. That was the entire mechanism. Users in two other countries began seeing columns belonging to a document type that does not exist in their country, and because the list was editable, a stray click could modify a record.

    
There is no clever fix. You set an explicit low priority on any new view that is not meant to become the default. But I would never have predicted that an alphabetical tiebreak could reassign a screen used by four companies, and no amount of testing my own feature would have caught it, because from where I sat the feature worked perfectly.

    
> 
::: note
**The generalisable lesson:** after a major upgrade, the failures that raise errors get fixed in days because the system tells you about them. The failures that change behaviour without raising anything can persist for months, because everyone's mental model says the code "works" — and it does run, it just no longer does what it says. After an upgrade, the right question is not "what broke?" but "what is still running and now means something different?"
:::

    
## What I do differently now

    
**I treat silence as unverified, not as success.** If a routine reports that it processed records, I check the count. A job that says "done" having done nothing is the single most expensive state a system can be in.

    
**I check the day-after logs, not the hour-after logs.** Anything that runs on a nightly schedule will fail a day later than the change that caused it, by which time everyone has moved on.

    
**I document each discovery as a rule, not as an anecdote.** Every one of these became a written note in the repository, phrased as something to check rather than something that happened. Whoever inherits this system should not have to rediscover that an alphabetical tiebreak can hijack a screen.

    
**And I built the monitoring that would have caught most of them.** That is the [other piece of work](./health-check.html) — a set of detectors that reconcile what the system believes against what the accounting says, on a schedule, so that the discovery mechanism stops being a user noticing something odd weeks later.
