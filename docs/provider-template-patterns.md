# uHOME-empire Provider Template Patterns

## Purpose

Capture reusable provider-template shapes from the archived Empire webhook
templates and adapt them for the v2 `uHOME-empire` contract lane.

## Why Keep This

The old template files are useful because they express:

- source system
- event type
- target entity
- field mapping
- required-field expectations

That pattern still fits the new `uHOME-empire` webhook lane even though the old
module layout does not.

## Recommended Mapping Template Shape

Use a small inspectable mapping document or JSON object that records:

```yaml
label: string
source_system: string
event_type: string
target_scope: string
target_entity: string
template_version: integer
field_map:
  remote_field: local_field
required_fields: [string]
notes: string
```

## Example: HubSpot Contact To Local Master

```yaml
label: HubSpot Contact To Local Master
source_system: hubspot
event_type: contact.updated
target_scope: local-master
target_entity: contact
template_version: 1
field_map:
  prefix_salutation: salutation
  firstname: given_name
  lastname: family_name
  company: organization
  jobtitle: job_title
  email: primary_email
  phone: phone
  mobilephone: mobile_phone
  fax: fax_number
  website: website_url
  twitterhandle: twitter_username
  address: street_address
  city: city
  state: state
  zip: postcode
  country: country
required_fields:
  - firstname
  - lastname
  - email
notes: Use for HubSpot contact webhook payloads routed into the app-owned local contact base and keep it aligned with standard iCloud contact fields.
```

## Rule

Mapping templates should help normalize remote payloads into local reviewable
records.

They should not imply that the remote provider becomes the source of truth.

## Active Repo Anchors

Current extracted v2 templates:

- `src/webhooks/mappings/default-contact-master.json`
- `src/webhooks/mappings/google-lead-enrichment.json`
- `src/webhooks/mappings/calendar-followup-task.json`
