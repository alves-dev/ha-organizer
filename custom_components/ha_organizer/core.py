"""Pure, deterministic audit engine. It deliberately knows nothing about HA I/O."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re
from typing import Any
import unicodedata

MODULE_LABELS = {
    "categories": "Categories",
    "areas": "Areas",
    "zones": "Zones",
    "labels": "Labels",
    "entity_ids": "Entity IDs",
    "exposed": "Exposed & Aliases",
}


def normalize(
    value: Any, *, case_insensitive=True, ignore_accents=True, normalize_separators=True
) -> str:
    text = str(value or "").strip()
    if ignore_accents:
        text = "".join(
            c
            for c in unicodedata.normalize("NFKD", text)
            if not unicodedata.combining(c)
        )
    if normalize_separators:
        text = re.sub(r"[-_\s]+", " ", text)
    return text.casefold() if case_insensitive else text


def fingerprint(
    module: str, item_id: str, relevant: Any, rule_versions: dict | None = None
) -> str:
    def canonical(value):
        if isinstance(value, dict):
            return {str(k): canonical(value[k]) for k in sorted(value)}
        if isinstance(value, (list, tuple)):
            return [canonical(v) for v in value]
        if isinstance(value, set):
            return sorted(canonical(v) for v in value)
        return value

    payload = {
        "module": module,
        "item_id": item_id,
        "rules": rule_versions or {},
        "data": canonical(relevant),
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )
    return "sha256:" + sha256(encoded.encode()).hexdigest()


@dataclass
class Finding:
    rule_id: str
    severity: str
    message: str
    resource_refs: list[str]


def _status(findings: list[Finding], attention=False) -> str:
    return (
        "non_compliant"
        if findings and any(f.severity == "error" for f in findings)
        else ("attention" if findings or attention else "compliant")
    )


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


def _groups(items: list[dict], key_fn):
    groups = {}
    for item in items:
        groups.setdefault(key_fn(item), []).append(item)
    return groups


def categories(snapshot: dict, settings=None) -> list[dict]:  # noqa: PLR0912
    settings = settings or {}
    settings = {
        "scopes": ["automation", "script"],
        "require_icon": False,
        "min_length": 0,
        "language": "any",
        "case_policy": "any",
        "allow_spaces": True,
        "allow_punctuation": True,
        **settings,
    }
    normalization = settings.get("normalization", {})

    def normalizer(value):
        return normalize(value, **normalization)

    configured_scopes = settings.get("scopes", ["automation", "script"])
    scopes = configured_scopes or ["automation", "script"]
    compare = settings.get("compare", len(configured_scopes) > 1)
    sources = {scope: snapshot.get("categories", {}).get(scope, []) for scope in scopes}
    rows = {}
    for scope, values in sources.items():
        for value in values:
            raw = value if isinstance(value, str) else value.get("name", "")
            key = normalizer(raw) if compare else f"{scope}:{normalizer(raw)}"
            row = rows.setdefault(
                key,
                {
                    "names": set(),
                    "scopes": {},
                    "resources": {},
                    "icons": set(),
                    "icons_by_scope": {},
                },
            )
            row["names"].add(raw)
            row["icons_by_scope"][scope] = (
                value.get("icon") if isinstance(value, dict) else None
            )
            if isinstance(value, dict) and value.get("icon"):
                row["icons"].add(value["icon"])
            row["scopes"][scope] = True
            row["resources"].setdefault(scope, []).append(value)
    result = []
    for key, row in rows.items():
        findings = []
        if len(row["names"]) > 1:
            findings.append(
                Finding(
                    "category_name_variants",
                    "warning",
                    "Nomes diferentes após normalização",
                    sorted(row["names"]),
                )
            )
        missing = (
            [scope for scope in scopes if not row["scopes"].get(scope)]
            if compare
            else []
        )
        if missing:
            findings.append(
                Finding(
                    "category_required_in_selected_scopes",
                    "warning",
                    f"Ausente em: {', '.join(missing)}",
                    missing,
                )
            )
        if (
            compare
            and len(row["icons_by_scope"]) > 1
            and len(set(row["icons_by_scope"].values())) > 1
        ):
            findings.append(
                Finding(
                    "category_icon_variants",
                    "warning",
                    "Ícones diferentes entre automações e scripts",
                    sorted(row["names"]),
                )
            )
        category_name = sorted(row["names"])[0]
        if settings["require_icon"] and not row["icons"]:
            findings.append(
                Finding(
                    "category_icon_required",
                    "warning",
                    "Categoria sem ícone",
                    sorted(row["names"]),
                )
            )
        if settings["min_length"] and len(category_name) < settings["min_length"]:
            findings.append(
                Finding(
                    "category_min_length",
                    "warning",
                    f"Nome menor que {settings['min_length']} caracteres",
                    sorted(row["names"]),
                )
            )
        if (
            settings["case_policy"] == "lowercase"
            and category_name != category_name.lower()
        ):
            findings.append(
                Finding(
                    "category_case_policy",
                    "warning",
                    "Nome deve usar apenas minúsculas",
                    sorted(row["names"]),
                )
            )
        if (
            settings["case_policy"] == "uppercase"
            and category_name != category_name.upper()
        ):
            findings.append(
                Finding(
                    "category_case_policy",
                    "warning",
                    "Nome deve usar apenas maiúsculas",
                    sorted(row["names"]),
                )
            )
        if not settings["allow_spaces"] and any(
            char.isspace() for char in category_name
        ):
            findings.append(
                Finding(
                    "category_spaces_policy",
                    "warning",
                    "Espaços não são permitidos no nome",
                    sorted(row["names"]),
                )
            )
        if not settings["allow_punctuation"] and any(
            not char.isalnum() and not char.isspace() for char in category_name
        ):
            findings.append(
                Finding(
                    "category_punctuation_policy",
                    "warning",
                    "Pontuação não é permitida no nome",
                    sorted(row["names"]),
                )
            )
        if settings["language"] != "any" and any(
            char.isalpha() and "LATIN" not in unicodedata.name(char, "")
            for char in category_name
        ):
            findings.append(
                Finding(
                    "category_language_policy",
                    "warning",
                    "Nome não parece usar o alfabeto esperado para "
                    f"{settings['language']}",
                    sorted(row["names"]),
                )
            )
        result.append(
            _item(
                "categories",
                key,
                category_name,
                {
                    "names": sorted(row["names"]),
                    "scopes": row["scopes"],
                    "resources": row["resources"],
                    "icons": sorted(row["icons"]),
                },
                findings,
                scopes=row["scopes"],
                resources=row["resources"],
                icon=next(iter(sorted(row["icons"])), None),
            )
        )
    return result


def areas(snapshot: dict, settings=None) -> list[dict]:
    settings = settings or {}

    def normalizer(value):
        return normalize(value, **settings.get("normalization", {}))

    values = snapshot.get("areas", [])
    result = []
    by_name = _groups(values, lambda x: normalizer(x.get("name")))
    for area in values:
        aid = area.get("id") or area.get("area_id") or normalize(area.get("name"))
        findings = []
        same = by_name.get(normalizer(area.get("name")), [])
        if len(same) > 1:
            findings.append(
                Finding(
                    "duplicate_area_name",
                    "error",
                    "Nome de área duplicado após normalização",
                    [x.get("id", x.get("area_id", "")) for x in same],
                )
            )
        devices = area.get("devices", [])
        entities = area.get("entities", [])
        result.append(
            _item(
                "areas",
                aid,
                area.get("name", aid),
                {
                    "name": area.get("name"),
                    "floor": area.get("floor"),
                    "devices": devices,
                    "entities": entities,
                },
                findings,
                **{k: area.get(k, []) for k in ("devices", "entities")},
                floor=area.get("floor"),
            )
        )
    for device in snapshot.get("devices_without_area", []):
        did = "device:" + str(device.get("id", device))
        result.append(
            _item(
                "areas",
                did,
                f"Dispositivo sem área: {device.get('name', did)}",
                device,
                [
                    Finding(
                        "device_without_area",
                        "attention",
                        "Dispositivo sem área",
                        [did],
                    )
                ],
                attention=True,
                devices=[device],
            )
        )
    return result


def zones(snapshot: dict, settings=None) -> list[dict]:
    settings = {
        "detect_duplicate_geometry": True,
        "min_radius": 0,
        "max_radius": 0,
        "require_icon": False,
        **(settings or {}),
    }
    values = snapshot.get("zones", [])
    result = []
    by_center = {}
    for z in values:
        by_center.setdefault(
            (z.get("latitude"), z.get("longitude"), z.get("radius")), []
        ).append(z)
    for z in values:
        zid = z.get("id") or z.get("zone_id") or z.get("name")
        findings = []
        dup = [
            x
            for x in by_center[(z.get("latitude"), z.get("longitude"), z.get("radius"))]
            if x is not z
        ]
        if (
            settings["detect_duplicate_geometry"]
            and dup
            and str(zid).casefold() != "home"
        ):
            findings.append(
                Finding(
                    "duplicate_zone_geometry",
                    "error",
                    "Zona com centro e raio idênticos",
                    [str(x.get("id", x.get("name"))) for x in dup],
                )
            )
        if not z.get("name"):
            findings.append(
                Finding("zone_name_missing", "warning", "Zona sem nome", [str(zid)])
            )
        if settings["require_icon"] and not z.get("icon"):
            findings.append(
                Finding(
                    "zone_icon_required", "info", "Zona sem ícone", [str(zid)]
                )
            )
        if settings["min_radius"] and (z.get("radius") or 0) < settings["min_radius"]:
            findings.append(
                Finding(
                    "zone_min_radius",
                    "warning",
                    f"Raio menor que {settings['min_radius']} m",
                    [str(zid)],
                )
            )
        if settings["max_radius"] and (z.get("radius") or 0) > settings["max_radius"]:
            findings.append(
                Finding(
                    "zone_max_radius",
                    "warning",
                    f"Raio maior que {settings['max_radius']} m",
                    [str(zid)],
                )
            )
        result.append(
            _item(
                "zones",
                zid,
                z.get("name") or zid,
                {
                    k: z.get(k)
                    for k in (
                        "name",
                        "latitude",
                        "longitude",
                        "radius",
                        "passive",
                        "icon",
                    )
                },
                findings,
                latitude=z.get("latitude"),
                longitude=z.get("longitude"),
                radius=z.get("radius"),
                passive=z.get("passive"),
                icon=z.get("icon"),
            )
        )
    return result


def labels(snapshot: dict, settings=None) -> list[dict]:
    settings = {"min_name_length": 1, "min_description_length": 0, **(settings or {})}

    def normalizer(value):
        return normalize(value, **settings.get("normalization", {}))

    values = snapshot.get("labels", [])
    by_name = _groups(values, lambda item: normalizer(item.get("name")))
    result = []
    for label in values:
        label_id = label.get("id") or label.get("name")
        findings = []
        name = label.get("name") or label_id
        description = label.get("description") or ""
        if len(name.strip()) < settings["min_name_length"]:
            findings.append(
                Finding(
                    "label_name_length",
                    "warning",
                    "Label name is shorter than the configured minimum",
                    [str(label_id)],
                )
            )
        if len(description.strip()) < settings["min_description_length"]:
            findings.append(
                Finding(
                    "label_description_length",
                    "warning",
                    "Label description is shorter than the configured minimum",
                    [str(label_id)],
                )
            )
        matching = by_name.get(normalizer(label.get("name")), [])
        if len(matching) > 1:
            findings.append(
                Finding(
                    "duplicate_label_name",
                    "error",
                    "Label name is duplicated after normalization",
                    [str(item.get("id")) for item in matching],
                )
            )
        result.append(
            _item(
                "labels",
                label_id,
                name,
                label,
                findings,
                icon=label.get("icon"),
                color=label.get("color"),
                description=description,
            )
        )
    return result


def entity_ids(snapshot: dict, settings=None) -> list[dict]:
    settings = settings or {}
    pattern = settings.get("pattern", "{domain}.{area}_{device}_{entity}")
    excluded = set(settings.get("excluded_domains", []))
    result = []
    for entity in snapshot.get("entities", []):
        eid = entity.get("entity_id", "")
        domain = eid.split(".", 1)[0] if "." in eid else ""
        findings = []
        expected = None
        if domain not in excluded:
            parts = eid.split(".", 1)
            tokens = re.split(r"[_\s-]+", parts[1] if len(parts) > 1 else "")
            if not domain or not parts[1] or re.search(r"(?:_\d+)$", eid):
                findings.append(
                    Finding(
                        "entity_id_format",
                        "warning",
                        "Entity ID fora do formato esperado ou com sufixo automático",
                        [eid],
                    )
                )
            expected = (
                pattern.replace("{domain}", domain)
                .replace(
                    "{area}",
                    normalize(entity.get("area_name") or "area").replace(" ", "_"),
                )
                .replace(
                    "{device}",
                    normalize(entity.get("device_name") or "device").replace(" ", "_"),
                )
                .replace("{entity}", tokens[-1] if tokens else "entity")
            )
            if expected != eid:
                findings.append(
                    Finding(
                        "entity_id_pattern",
                        "warning",
                        "Entity ID não segue o padrão configurado",
                        [eid],
                    )
                )
        result.append(
            _item(
                "entity_ids",
                eid,
                eid,
                {
                    "entity_id": eid,
                    "name": entity.get("name"),
                    "area": entity.get("area_id"),
                    "device": entity.get("device_id"),
                    "platform": entity.get("platform"),
                },
                findings,
                entity=entity,
                expected=expected,
                policy=pattern,
            )
        )
    return result


def exposed(snapshot: dict, settings=None) -> list[dict]:
    settings = settings or {}

    def normalizer(value):
        return normalize(value, **settings.get("normalization", {}))

    values = snapshot.get("exposed", [])
    entities = {}
    entries_by_key = {}
    keys_by_entity = {}
    for value in values:
        eid = value.get("entity_id", "")
        names = [
            value.get("name") or value.get("friendly_name") or "",
            *(value.get("aliases") or []),
        ]
        names = list(dict.fromkeys(name for name in names if name))
        if not eid or not names:
            continue
        entities[eid] = names
        for name in names:
            key = normalizer(name)
            entries_by_key.setdefault(key, []).append((eid, name))
            keys_by_entity.setdefault(eid, set()).add(key)

    result = []
    unvisited = set(entries_by_key)
    while unvisited:
        start = unvisited.pop()
        component = {start}
        pending = [start]
        while pending:
            key = pending.pop()
            entity_ids = {eid for eid, _ in entries_by_key[key]}
            linked = {
                linked_key
                for eid in entity_ids
                for linked_key in keys_by_entity[eid]
            }
            new_keys = linked & unvisited
            component.update(new_keys)
            unvisited -= new_keys
            pending.extend(new_keys)

        entries = [
            entry
            for key in component
            for entry in entries_by_key[key]
        ]
        refs = sorted({eid for eid, _ in entries})
        title = next(entities[eid][0] for eid in refs)
        key = normalizer(title)
        findings = []
        if len(refs) > 1:
            findings.append(
                Finding(
                    "exposed_name_collision",
                    "error",
                    "Nome ou alias exposto colide com outra entidade",
                    refs,
                )
            )
        relevant = {
            "key": key,
            "entries": [
                {"entity_id": eid, "name": name} for eid, name in entries
            ],
        }
        result.append(
            _item(
                "exposed",
                key,
                title,
                relevant,
                findings,
                entities=refs,
                entries=relevant["entries"],
            )
        )
    return result


GENERATORS = {
    "categories": categories,
    "areas": areas,
    "zones": zones,
    "labels": labels,
    "entity_ids": entity_ids,
    "exposed": exposed,
}


def apply_reviews(items: list[dict], reviews: dict) -> list[dict]:
    for item in items:
        review = reviews.get(item["item_key"])
        status = "pending"
        if review:
            status = review.get("review_status", "pending")
            if (
                status in ("reviewed", "ignored")
                and review.get("reviewed_fingerprint") != item["fingerprint"]
            ):
                status = "stale"
        item["review_status"] = status
        item["review"] = review or None
    return items


def scan(snapshot: dict, config: dict, reviews=None) -> dict:
    reviews = reviews or {}
    modules = {}
    for module, options in config.get("modules", {}).items():
        if options.get("enabled", True):
            settings = options.get("settings", {})
            if module == "categories":
                settings = {**config.get("categories", {}), **settings}
            if module == "zones":
                settings = {**config.get("zones", {}), **settings}
            if module == "labels":
                settings = {**config.get("labels", {}), **settings}
            if module == "entity_ids":
                settings = {
                    "pattern": config.get("entity_id_pattern", "{domain}.{entity}"),
                    "excluded_domains": config.get("excluded_domains", []),
                    **settings,
                }
            modules[module] = apply_reviews(
                GENERATORS[module](snapshot, settings), reviews
            )
    return {"modules": modules}


def overview(result: dict) -> dict:
    all_items = [i for values in result.get("modules", {}).values() for i in values]
    total = len(all_items)
    current = [
        i for i in all_items if i.get("review_status") in ("reviewed", "ignored")
    ]

    def counts(field):
        return {
            value: sum(i.get(field) == value for i in all_items)
            for value in (
                "compliant",
                "non_compliant",
                "attention",
                "not_applicable",
                "pending",
                "reviewed",
                "ignored",
                "stale",
            )
        }

    module_progress = {}
    for module, items in result.get("modules", {}).items():
        reviewed = sum(
            item.get("review_status") in ("reviewed", "ignored")
            for item in items
        )
        module_progress[module] = {
            "total": len(items),
            "reviewed": reviewed,
            "progress": reviewed / len(items) if items else 1,
        }

    return {
        "total": total,
        "review_progress": len(current) / total if total else 1,
        "compliance": counts("compliance_status"),
        "review": counts("review_status"),
        "stale": [i for i in all_items if i.get("review_status") == "stale"],
        "module_progress": module_progress,
    }
