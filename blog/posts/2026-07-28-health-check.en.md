---
title: Alert quality beats alert count
subtitle: Building a health check for an ERP running four companies in three countries
date: 2026-07-28
lang: en
slug: health-check
summary: Building a health check that reconciles inventory against the general ledger every six hours, what it found that no report showed, and why an alert nobody acts on is a defect rather than a nuisance.
tags: monitoring, erp, observability
---

For a long time, the way we found out that something was wrong with our ERP was that somebody complained.

    
An accountant would notice, closing the month, that inventory and the general ledger disagreed. A salesperson would find that an electronic invoice had been rejected by the tax authority weeks earlier and had been sitting in a queue ever since. Someone would discover on a Wednesday that the authorised range of invoice numbers for a document type had run out — which in a regulated invoicing regime means you simply cannot invoice until the regulator issues more.

    
Every one of those was findable in advance. None of them was found in advance, because nothing was looking.

    
## Chasing bugs versus building the thing that finds them

    
My first instinct was to fix each problem as it appeared. That is satisfying and it does not scale. Each fix addressed one instance of a class of failure I could not enumerate, and the interval between the failure happening and anyone noticing stayed exactly the same — weeks.

    
So I stopped fixing individual cases and built a health check instead: a scheduled routine that interrogates the system on a fixed cadence and reports what it finds to the people who can act on it. It now runs around forty-six detectors every six hours, with a smaller urgent subset every thirty minutes.

    
What the detectors look at falls into four groups:

    
- **Reconciliation.** The inventory ledger and the accounting must tell the same story. For each country and each relevant account, the detector computes both sides and compares them against a threshold appropriate to that currency. Divergence is reported with the transactions that caused it, not just a number.

      - **Regulatory state.** Documents rejected by a tax authority, documents stuck waiting to be sent, and the projected exhaustion date of each authorised numbering range — so that "we run out of invoice numbers in nine days" is something we learn nine days early rather than on the day.

      - **System health.** Real errors in the server log, separated from noise, plus the scheduled jobs that have started failing.

      - **Business pulse.** A per-country digest of what actually moved. Not for alerting — for context, so that an anomaly can be read against a normal day.

    
## The thing it found

    
The first meaningful run surfaced something nobody knew about: inventory cost was being recorded twice for one category of transaction. Two independent parts of the system — a physical stock movement and a settlement process — were each doing their honest job, and both were crediting the same accounting entry.

    
It had been accumulating for more than a year. No report showed it, because every individual report was internally consistent; the discrepancy only existed *between* two views that nobody had ever put side by side. That is precisely the class of problem a human reviewer never finds, because finding it requires comparing two things that each look correct.

    
Two things came out of that. The historical figures were corrected, and — more importantly — the reconciliation became permanent. The same comparison now runs every six hours, so if the conditions that allowed it ever return, we find out that day instead of the following year.

    
## The rule that made it work

    
The temptation with a system like this is to measure it by coverage: how many detectors, how many alerts. That is the wrong metric, and following it produces something worse than nothing.

    
> 
Every alert has to produce an action. If an alert fires and the correct response is to ignore it, that is a defect in my detector — not a nuisance to be tolerated.

    
I enforced this literally. Any detector that produced an alert nobody acted on got rewritten or deleted. The reasoning is simple: a channel that cries wolf trains people to ignore it, and the cost is not the wasted attention — it's the one real alert that gets ignored along with the noise. A monitoring system with a hundred detectors that people skim is strictly worse than one with ten they read.

    
## Where I was wrong

    
One of my own detectors was the best argument for this rule.

    
I built one to find duplicated inventory records, using the identifying key that the platform uses as standard. It reported thousands of duplicates. I was convinced I had found something large.

    
I was wrong, and dangerously so. Our consignment warehouses separate stock by dimensions the standard key does not include — which customer's premises it sits in, and which company owns it. Records that looked identical under the standard key were legitimately distinct records for different stores. Acting on my own alert would have merged inventory belonging to different customers into a single pile: a far worse problem than the one I thought I was fixing.

    
When I re-ran the comparison with the correct key, the count was zero. There had never been a problem. The detector was rewritten, and the constraint was written down in bold so that nobody — including future me — repeats it.

    
I keep coming back to this one, because I did everything right procedurally: I noticed an anomaly, quantified it, and prepared a fix. What saved us was a colleague pushing back and my checking before acting. Confidence in a finding is not evidence for it.

    
## What success actually looks like

    
Not a dashboard. The measurable outcome is unglamorous: the reconciliation between inventory and the general ledger stays within threshold in each country, the digest arrives and is mostly boring, and when it isn't, someone acts on it that morning.

    
The signal I trust most is behavioural. People now check the alert before they check the system. The discovery mechanism stopped being a user noticing something odd weeks later — and that shift, not the detector count, is the whole point.
