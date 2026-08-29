# Pattern: Canonical Findings and Stale Reviews

## Description

Represent every audited resource as a canonical item with findings, calculated compliance, and a stable fingerprint. Apply the saved human review after generation so review state remains independent from the calculated result.

## When to Use

Use this when adding an audit module or rule whose results can be reviewed over time and should become stale only when relevant data changes.

## Pattern

Create only deterministic relevant data for an item. Canonicalize unordered dictionaries and sets before creating a fingerprint. Generate findings first, then apply saved reviews by comparing the current fingerprint with the saved one.

## Example

```python
def _item(module, item_id, title, relevant, findings=None, **extra):
    findings = findings or []
    return {
        "item_key": f"{module}:{item_id}",
        "module": module,
        "id": item_id,
        "title": title,
        "compliance_status": _status(findings, extra.pop("attention", False)),
        "fingerprint": fingerprint(module, item_id, relevant),
        "findings": [asdict(f) for f in findings],
        **extra,
    }

def apply_reviews(items, reviews):
    for item in items:
        review = reviews.get(item["item_key"])
        status = "pending"
        if review:
            status = review.get("review_status", "pending")
            if status in ("reviewed", "ignored") and review.get(
                "reviewed_fingerprint"
            ) != item["fingerprint"]:
                status = "stale"
        item["review_status"] = status
    return items
```

## Files Using This Pattern

- [core.py](../../../custom_components/ha_organizer/core.py) - generates canonical items, fingerprints, compliance, and review state.
- [storage.py](../../../custom_components/ha_organizer/storage.py) - persists review status and the reviewed fingerprint.
- [websocket.py](../../../custom_components/ha_organizer/websocket.py) - accepts and persists administrator review actions.

## Related

- [Decision: Deterministic Audit and Review Model](../../decisions/002-deterministic-audit-and-review-model.md)
- [Feature: Overview and Review Progress](../../intent/feature-overview-and-review-progress.md)

## Status

- **Created**: 2026-08-28
- **Status**: Active
