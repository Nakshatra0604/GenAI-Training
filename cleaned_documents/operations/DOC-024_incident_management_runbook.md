## 1. Purpose

This runbook describes how NexaCore Solutions operations teams respond to
service-affecting incidents, distinct from the security-specific Incident
Response Procedure, which covers security breaches rather than general
service outages.

## 2. Detecting an Incident

Most incidents are detected automatically through monitoring alerts, though
some are first reported by customers through support. Any employee who
notices unusual behavior, such as a service being unreachable, should
report it in the #ops-incidents channel even if they are unsure whether it
qualifies as an incident.

## 3. Declaring an Incident

An on-call engineer declares an incident by posting in the incident channel
and creating an incident record, which assigns an incident commander
responsible for coordinating the response. Declaring early, even before the
full scope is known, is preferred over waiting for certainty.

## 4. Roles During an Incident

- Incident commander: coordinates response, makes final decisions, manages communication
- Technical lead: directs the technical investigation and fix
- Communications lead: updates the status page and internal stakeholders

Not every incident requires all three roles; smaller incidents may be
handled by a single engineer acting in all capacities.

## 5. Severity Levels

| Severity | Description | Update frequency |
|---|---|---|
| SEV1 | Complete outage of a core service | Every 15 minutes |
| SEV2 | Significant degradation affecting many customers | Every 30 minutes |
| SEV3 | Limited impact affecting a subset of customers | Every 2 hours |

## 6. Status Page Updates

For SEV1 and SEV2 incidents, the status page is updated within fifteen
minutes of declaration and kept current throughout the incident. Status
page updates avoid speculating about root cause until it is reasonably
well understood, to avoid needing frequent corrections.

## 7. Resolution

An incident is resolved once the service has returned to normal operation
and this has been confirmed through monitoring, not just through the fix
being deployed. The incident commander formally closes the incident record
once resolution is confirmed.

## 8. Post-Incident Review

A post-incident review is held within five business days for SEV1 and
SEV2 incidents, producing a written summary of timeline, impact, root
cause, and follow-up actions with owners and due dates. Reviews are
blameless and focus on system and process gaps.