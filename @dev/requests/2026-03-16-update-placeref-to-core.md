# Action: Update PlaceRef Usage to Core Contract

The PlaceRef contract is now published in uDOS-core/contracts/ as the canonical source for spatial and file-location references.

## Required Action
- Update all PlaceRef parsing, validation, and schema references in your repo to use the Core contract.
- Do not copy or duplicate the contract—reference it directly or via documentation.
- Do not move spatial datasets or registries into Core. Grid remains the owner of spatial truth.

## Reference
- uDOS-core/contracts/place_ref_contract.json
- uDOS-core/contracts/place_ref_contract.md

Contact uDOS-core maintainers with questions or for migration support.

---

This request is issued to all sibling repo maintainers: uDOS-grid, uDOS-shell, uDOS-wizard, uHOME-server, uHOME-empire, uDOS-gameplay.