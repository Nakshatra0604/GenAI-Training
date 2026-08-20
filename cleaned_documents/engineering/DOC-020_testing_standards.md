## Testing Philosophy

Tests exist to give engineers confidence to change code without manually
re-verifying every behavior each time. A change without adequate test
coverage should be treated as incomplete, not as something to be tested
manually before every future release.

## Unit Tests

Unit tests cover individual functions or small units of logic in
isolation, with external dependencies replaced by test doubles. Unit tests
should run quickly, typically in well under a second each, so they can be
run frequently during development.

## Integration Tests

Integration tests verify that multiple components work together correctly,
such as a service and its database. These are slower than unit tests and
are typically run in continuous integration rather than on every local
save.

## End-to-End Tests

A small number of end-to-end tests cover critical user flows from the
perspective of an actual user, such as completing a purchase. End-to-end
tests are the most expensive to maintain, so they are reserved for flows
where a failure would have significant business impact.

## Coverage Expectations

There is no single required coverage percentage; instead, coverage
expectations scale with risk. Payment processing and authentication code
require thorough test coverage, while low-risk internal tooling may
reasonably have lighter coverage.

## Flaky Tests

A test that fails intermittently without a code change is considered
broken and should be fixed or removed promptly rather than left in place
and ignored, since flaky tests erode trust in the overall test suite over
time.