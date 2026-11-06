<!--
PR title: use a Conventional Commit, for example `feat: add a Grafana dashboard` or `fix: keep trace_id in error logs`.
PRs are squash-merged, so the title becomes the commit message on master.
-->

## Summary

<!-- What does this PR change? Why is the change needed? -->

## Test plan

* [ ] I ran `just check` (lint, format, lock file, workflow audit)
* [ ] I ran `just test`
* [ ] I started the stack with `just up` and checked the affected telemetry in Grafana, if applicable
