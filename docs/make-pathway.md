# uHOME-empire Make Pathway

## Purpose

The Make pathway is the educational side of Empire. It should help users run a
workflow, inspect how it works, modify it safely, and eventually build or share
their own pack.

Empire should not hide operational structure behind a polished black box. Users
need to see how jobs, templates, mappings, channels, approvals, and outputs fit
together.

## Learning Ladder

### Level 1: Run

User selects a prebuilt pack and:

- fills required inputs
- previews outputs
- performs a dry-run
- passes approval gates
- executes the workflow

### Level 2: Modify

User edits:

- templates
- fields and mappings
- timing or channel choices
- audience rules
- asset references
- publish targets

### Level 3: Build

User creates:

- a new pack
- a new template family
- a new transform
- a new script chain
- a new provider mapping

### Level 4: Share Or Deploy

User:

- packages the pack or binder
- saves it into a library
- shares it to a team or community
- promotes it to a stable workflow

## What Users Should Be Able To Inspect

- job manifests
- input and output contracts
- template variables
- audience or contact flow
- channel differences
- dry-run behavior
- approval gates
- execution logs and reports

## Audience Levels

The pathway should support:

- beginners using guided starter packs
- intermediate users editing manifests and mappings
- advanced users building full containers or script packs

## Current Repo Direction

The current family implementation already supports the contract loop for:

- sync package generation
- automation job queueing
- processing and result retrieval through `uHOME-server`

The next repo evolution should make those seams more visible as learnable pack
structure rather than keeping them as adapter-only internals.
