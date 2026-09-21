# Orbital Dynamics Co. — Internal Handbook

A short sample knowledge base for testing the RAG pipeline.

## Expense Policy

Employees may spend up to $75 per day on meals while travelling without
pre-approval. Anything above that needs written sign-off from a manager before
the trip, not after. Receipts must be submitted within 14 days of returning;
claims filed later than 30 days are rejected outright. Alcohol is never
reimbursable, including on client dinners.

## Remote Work

The company is remote-first. Employees are expected to be reachable between
10:00 and 15:00 in their local time zone, and the rest of the day is theirs to
schedule. Everyone is asked to come to the Lisbon office twice a year: once in
March for planning, once in October for the engineering summit. Travel for
those two trips is booked centrally and does not count against the expense
policy's daily limit.

## Deployment Process

Production deploys happen on Tuesdays and Thursdays between 09:00 and 11:00
UTC. Every deploy needs a green CI run and one approving review from someone
outside the author's team. Friday deploys are blocked by tooling; overriding
the block requires the on-call engineer and the CTO to both approve in the
#deploys channel. Rollbacks do not need approval — anyone on call can trigger
one immediately.

## On-Call Rotation

The on-call rotation is one week long and runs Wednesday to Wednesday. Each
rotation has a primary and a secondary engineer. The primary must acknowledge a
page within 10 minutes; if they do not, it escalates to the secondary after 15
minutes, and to the engineering manager after 30. Anyone who is paged outside
09:00–18:00 local time gets a compensation day, claimed by filing a ticket in
the People queue.

## Vacation and Leave

Paid vacation is 25 days per year, accruing monthly, and up to 5 unused days
carry into the following year. Requests longer than 5 consecutive days should
be filed at least three weeks in advance. Sick leave is not counted against
vacation and does not need a doctor's note for the first three days.
