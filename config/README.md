# Config

`config/` is the checked-in configuration lane for `uHOME-empire`.

Family placement rule:

- put checked-in non-secret config templates and config examples here
- keep starter sync payloads and workflow samples in `examples/`
- reserve `defaults/` for reusable defaults only, not illustrative samples

Current state:

- no separate operational config files are required yet
- repo validation is shell and Python standard-library based

Planned use of this root:

- sync workflow defaults
- Google and HubSpot configuration examples
