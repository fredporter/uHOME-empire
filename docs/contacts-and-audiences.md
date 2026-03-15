# uHOME-empire Contacts And Audiences

## Role

Empire owns audience-facing operational contact handling. It should not replace
the family canonical identity model, but it should own the pack-level and
channel-level handling needed for campaigns, outreach, segmentation, and CRM
work.

## Core Concepts

- contact
- company
- audience
- segment
- campaign
- message
- report

## Baseline Data Direction

Contact operations should support at least:

- name
- email
- phone
- address
- city
- postcode
- state
- country

Company operations should support at least:

- company name
- address
- city
- postcode
- state
- country
- phone
- linked contacts

## Operational Responsibilities

Empire should house:

- field mapping
- segmentation logic
- list hygiene
- dedupe and merge helpers
- tagging and grouping logic
- CRM-facing workflow packaging

## Matching Direction

Initial matching should stay simple and inspectable:

- email-address matching for email workflows
- phone-number matching for later text or WhatsApp style flows

## Boundaries

Empire does not own the family canonical contact graph contract. It owns the
operational handling required to turn that data into messaging, audience, and
campaign workflows.

## Related Docs

- `docs/contact-and-crm-model.md`
- `docs/provider-lane-status.md`
