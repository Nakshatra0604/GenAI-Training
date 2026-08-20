# Coding Standards

## General Principles

Code at NexaCore Solutions should favor clarity over cleverness. A
reviewer should be able to understand what a function does without needing
to run it, and naming should describe intent rather than implementation
detail.

## Formatting

All repositories use an automated formatter configured in the project's
root configuration file. Formatting is enforced in continuous integration,
so manual formatting debates during code review should not be necessary;
if the formatter allows a style engineers disagree with, the fix belongs
in the formatter configuration, not in individual pull requests.

## Function and File Size

Functions that grow beyond roughly fifty lines are a signal to consider
splitting responsibilities, though this is a guideline rather than a hard
rule enforced by tooling. Files that accumulate unrelated functionality
over time should be split during a natural refactor rather than left to
grow indefinitely.

## Error Handling

Errors should be handled at the layer that has enough context to decide
what to do about them. Swallowing an error silently is discouraged;
at minimum, an error should be logged with enough context to diagnose the
issue later.

## Related Tooling

## Comments

Comments should explain why a piece of code exists, not what it does when
the code itself is already clear. Comments describing what code does tend
to go stale as the code changes; comments explaining a non-obvious
constraint or trade-off tend to stay useful much longer.

## Dependencies



New third-party dependencies should be discussed with the team before
being added, particularly for anything that will be difficult to remove
later. Preference is given to dependencies that are actively maintained
and widely used over niche libraries with a single maintainer.
