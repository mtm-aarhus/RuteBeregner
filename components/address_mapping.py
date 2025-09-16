# components/address_mapping.py
"""
Hardkodet mapping for Modtageranlæg.

Denne modul erstatter tidligere "company_address_mapping" og dynamiske builds.
Slutadresser slås direkte op via ModtageranlægID.

For bagudkompatibilitet eksporterer modulet også:
- company_address_mapping: dict[str, dict[str, str]]
  (key = virksomhedsnavn, value indeholder både "address" og "end_address")
"""

from typing import Dict, Optional, Any, TypedDict, List


class ReceiverEntry(TypedDict):
    name: str
    address: str


# Hardkodet mapping: ModtageranlægID -> {name, address}
# Udvid listen efter behov.
receiver_mapping: Dict[int, ReceiverEntry] = {
    1061: {"name": "Gert Svith, Birkesig Grusgrav", "address": "Rugvænget 18, 8444 Grenå"},
    1013: {"name": "JJ Grus A/S (Kalbygård Grusgrav)", "address": "Hovedvejen 24A, 8670 Låsby"},
    1327: {"name": "Johs. Sørensen & Sønner A/S, Ren depotjord", "address": "Holmstrupgårdvej 9, 8220 Brabrand"},
    2191: {"name": "JJ Grus A/S (Ans)", "address": "Søndermarksgade 43, 8643 Ans"},
    1901: {"name": "EHJ Energi & Miljø A/S - Let forurenet jord", "address": "Hadstenvej 16, 8940 Randers SV"},
    # Tilføj flere som:
    # 9999: {"name": "Navn", "address": "Vejnavn 1, 1234 By"},
}


def _to_int(value: Any):  # Optional[int] i praksis
    try:
        if value is None or value == "":
            return None
        return int(float(value))
    except Exception:
        return None


def get_receiver_address_by_id(receiver_id: Any) -> str:
    """Returnér address (slut-adresse) for et givet ModtageranlægID."""
    rid = _to_int(receiver_id)
    if rid is None:
        return ""
    entry = receiver_mapping.get(rid)
    return entry["address"] if entry else ""


def get_receiver_name_by_id(receiver_id: Any) -> str:
    """Returnér virksomhedsnavn for et givet ModtageranlægID."""
    rid = _to_int(receiver_id)
    if rid is None:
        return ""
    entry = receiver_mapping.get(rid)
    return entry["name"] if entry else ""


def set_receiver_entry(receiver_id: Any, name: str, address: str) -> None:
    """Tilføj/ret en mapping (nemt at vedligeholde)."""
    rid = _to_int(receiver_id)
    if rid is None:
        return
    receiver_mapping[rid] = {"name": (name or "").strip(), "address": (address or "").strip()}


def remove_receiver_entry(receiver_id: Any) -> None:
    rid = _to_int(receiver_id)
    if rid is None:
        return
    receiver_mapping.pop(rid, None)


def get_all_receiver_ids() -> List[int]:
    return list(receiver_mapping.keys())


def get_receiver_record(receiver_id: Any) -> Dict[str, str]:
    rid = _to_int(receiver_id)
    if rid is None:
        return {}
    return dict(receiver_mapping.get(rid, {}))


# ---------------------------------------------------------------------------
# Bagudkompatibilitet: company_address_mapping (name -> {end_address, address})
# Nogle dele af appen importerer stadig:
#   from components.address_mapping import company_address_mapping
# Vi bygger derfor en navnebaseret mapping ud fra receiver_mapping.
# ---------------------------------------------------------------------------

company_address_mapping: Dict[str, Dict[str, str]] = {
    v["name"]: {"end_address": v["address"], "address": v["address"]}
    for v in receiver_mapping.values()
}

__all__ = [
    # Primær API
    "receiver_mapping",
    "get_receiver_address_by_id",
    "get_receiver_name_by_id",
    "set_receiver_entry",
    "remove_receiver_entry",
    "get_all_receiver_ids",
    "get_receiver_record",
    # Bagudkompatibelt alias
    "company_address_mapping",
]

