# uHOME-empire Contact And CRM Model

## Purpose

Define the v2 contact and CRM vocabulary for `uHOME-empire` without moving
canonical contact ownership out of the macOS desktop app.

## Ownership Split

### macOS app owns

- Apple Contacts sync
- local user contact database
- local binder contact database
- operator-facing contact editing and review

### `uHOME-empire` owns

- HubSpot sync for app-owned contact records
- task and note sync into HubSpot
- contact enrichment from remote systems
- dedupe, mapping, and CRM-side association maintenance
- console-style CRM visibility over synchronized records

### `uDOS-core` owns

- canonical workflow and task semantics
- binder and vault truth rules
- any family-wide contact or record contracts promoted later

## Core Rule

The source of truth for contact identity remains local and reviewable.

`uHOME-empire` may enrich, map, and synchronize contact records, but it should
not become a second hidden canonical contact store.

## Normalized Contact Shape

Recommended normalized contact fields for `uHOME-empire` sync lanes:

```yaml
contact_id: uuid
display_name: string
salutation: string|null
given_name: string|null
family_name: string|null
emails: [string]
phones: [string]
mobile_phone: string|null
fax_number: string|null
organization: string|null
job_title: string|null
website_url: string|null
twitter_username: string|null
street_address: string|null
city: string|null
state: string|null
postcode: string|null
country: string|null
binder_ids: [string]
source_systems: [apple_contacts, binder, hubspot, google, manual]
hubspot:
  contact_id: string|null
  company_ids: [string]
  owner_id: string|null
  sync_state: pending|synced|conflict|error
crm_flags:
  crm_relevant: bool
  requires_review: bool
```

## Sync Rules

### Upstream precedence

Use this precedence order unless a repo-specific runbook says otherwise:

1. reviewed local user or binder contact record
2. Apple Contacts-linked metadata
3. HubSpot enrichment fields
4. other remote projections

### Allowed `uHOME-empire` updates

- attach HubSpot identifiers
- append CRM-side metadata and activity state
- record sync health and conflict markers
- enrich organization or lifecycle data for review

### Disallowed `uHOME-empire` behavior

- silently replace the app-owned local contact record
- treat HubSpot as canonical identity truth
- bypass review when contact merges are ambiguous

## HubSpot Scope

The current `uHOME-empire` HubSpot lane should assume:

- contacts sync
- tasks sync
- notes sync
- company associations
- webhook-driven update intake

Deals, advanced marketing fields, and heavy CRM analytics should remain
optional until the public contract actually needs them.

## Binder Linkage

Contacts should remain binder-aware.

At minimum, synchronized CRM records should preserve:

- linked binder ids
- linked task ids where relevant
- document or note references used for CRM context
- last reviewed local source timestamp

## Review Model

Any merge or enrichment flow that changes identity-level fields should expose:

- source systems involved
- fields in conflict
- recommended resolution
- last sync status

This keeps CRM sync useful without moving human contact judgment into a hidden
background process.

## Shared Mapping Rule

When aligning HubSpot sync with the app-owned contact base, use the shared
field set carried by both HubSpot and standard iCloud contact surfaces:

- first name
- last name
- prefix or salutation
- company name
- job title
- email
- phone number
- mobile phone number
- fax number
- website URL
- Twitter username
- address fields: street, city, state, postcode, country
