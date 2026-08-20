# Git Branching Workflow

NexaCore Solutions engineering teams use a trunk-based workflow. The `main`
branch is always expected to be deployable, and all changes are made on
short-lived feature branches merged back into `main` through a reviewed
pull request.

## Branch Naming

Branches are named using the pattern `type/short-description`, where type
is one of `feature`, `fix`, `chore`, or `refactor`. For example,
`fix/login-timeout` or `feature/export-to-csv`. Branch names should be
short enough to read at a glance in a list of open branches.

## Commit Messages

Commit messages should describe the change in the imperative mood, for
example "Add retry logic to payment sync" rather than "Added retry logic."
The first line should be under seventy characters, with additional context
in the body if needed.

## Pull Requests

Pull requests should stay open for as short a time as possible to avoid
merge conflicts and diverging from `main`. Long-running feature branches
are discouraged; if a feature genuinely needs more than a few days, it
should be built incrementally behind a feature flag rather than as one
large branch.

## Merging

Branches are merged using a squash merge so that `main` maintains a clean,
readable history with one commit per pull request. Branches should be
deleted after merging to keep the repository's branch list manageable.

## Hotfixes

Urgent production fixes follow the same branch naming and review process
as any other change, but reviews may be expedited by pinging the on-call
engineer directly rather than waiting for the normal review queue.