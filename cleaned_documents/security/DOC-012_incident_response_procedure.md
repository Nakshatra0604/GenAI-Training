## 1. Purpose

This procedure describes how NexaCore Solutions detects, contains, and
recovers from security incidents, and how incidents are communicated
internally and, where required, externally.

## 2. What Counts as an Incident

An incident is any event that compromises the confidentiality, integrity,
or availability of company or customer data or systems. Examples include a
phishing email that leads to a compromised account, malware detected on a
device, an unauthorized access attempt, or accidental exposure of
Restricted data.

## 3. Reporting an Incident

Any employee who suspects a security incident should report it immediately
to IT Security through the incident hotline or the #security-incident
channel, rather than attempting to resolve it themselves. Early reporting,
even of something that turns out to be a false alarm, is always preferred
over delayed reporting.

## 4. Severity Levels

| Severity | Description | Initial response target |
|---|---|---|
| Critical | Active compromise affecting customer data or core systems | 15 minutes |
| High | Contained compromise of an internal system or account | 1 hour |
| Medium | Suspicious activity requiring investigation | 4 hours |
| Low | Policy violation with limited security impact | 1 business day |

## 5. Containment

Once an incident is confirmed, the responding team focuses first on
containment: isolating affected systems, disabling compromised accounts,
and preventing further spread, before moving to full investigation. Speed
of containment is prioritized over completeness of the initial
investigation.

## 6. Investigation

After containment, the security team investigates the root cause, scope of
affected data or systems, and timeline of events. Findings are documented
in an incident record that is used both for the final report and for any
required external notifications.

## 7. Communication

Internal stakeholders are updated at regular intervals appropriate to the
severity level. For incidents involving customer or regulated data, the
Legal and Communications teams are looped in early to assess notification
obligations, since requirements vary depending on the type of data and
jurisdiction involved.

## 8. Recovery

Systems are restored from clean backups or rebuilt from known-good
configurations rather than simply patched in place, when there is any
uncertainty about the extent of compromise. Recovery is only considered
complete once affected systems have passed a verification check by IT
Security.

## 9. Post-Incident Review

Within two weeks of resolution, the responding team holds a post-incident
review to document what happened, what worked well, and what should
change. This is a blameless review focused on process and system
improvement rather than assigning fault to an individual.

## 10. Recordkeeping

All incident records are retained for a minimum of three years and are
made available to auditors and regulators where legally required.