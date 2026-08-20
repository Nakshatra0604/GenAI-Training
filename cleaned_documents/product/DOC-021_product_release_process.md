## Release Cadence

NexaCore Solutions ships product updates on a two-week cycle for most
features, with critical fixes released outside the normal cycle as needed.
Larger features are typically rolled out gradually rather than released to
all customers at once.

## Release Readiness

A feature is considered ready for release once it has passed QA, has
documentation prepared for customer-facing changes, and has been reviewed
by the feature's product manager against the original requirements.
Features missing any of these are held to the next release rather than
shipped incomplete.

## Gradual Rollout

Significant changes are rolled out to an initial five percent of customers
for forty-eight hours before wider release, allowing the team to monitor
for unexpected issues at a manageable scale. Rollout is paused immediately
if error rates or customer support volume increases noticeably during this
window.

## Release Communication

Customer-facing changes are announced through the in-app changelog and, for
larger changes, an email to affected customers. Internal teams are notified
through the #product-releases channel so that customer support and sales
are aware of new functionality before customers start asking about it.

## Rollback

Any release can be rolled back by the on-call engineer without requiring
additional approval if it is causing a clear negative impact. A rollback is
followed by a short written summary of what happened and the plan for
re-release.