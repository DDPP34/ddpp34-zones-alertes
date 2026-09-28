#!/usr/bin/env python3
"""
DDPP34 - Synchronisation des statuts d'alerte des zones conchylicoles.

Lit la table Cumuls_Zones_Alertes du document Grist "Tableau de saisie_calcul_cumuls_pluvio_DDPP34"
et écrit un fichier zone-status.json (committé dans ce dépôt) contenant :
  - zoneStatus : dict {code_zone: [ {critere, station, jours, seuil, cumulActuel,
    alerte, inactif, prog}, ... ]}
  - syncedAt   : date/heure de la synchronisation, au format JJ/MM/AAAA HH:MM (Europe/Paris)

Ce fichier est ensuite lu par le tableau de bord REMI/REPHYTOX (via une simple requête
HTTP sur l'URL brute GitHub de ce dépôt) pour rafraîchir le panneau "Zones sous surveillance",
sans dépendre de Make.

Important : ce script ne fait AUCUN calcul de seuil ni de logique d'alerte — il se contente
de relire tels quels les champs déjà calculés côté Grist (colonnes Seuil / Alerte / CumulActuel).
"""

import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

GRIST_DOC_ID = "hEKSLCQ8fFRywVHN5juk5t"
GRIST_TABLE = "Cumuls_Zones_Alertes"
GRIST_BASE_URL = f"https://grist.numerique.gouv.fr/api/docs/{GRIST_DOC_ID}"
OUTPUT_FILE = "zone-status.json"


def fetch_records(token: str) -> list:
    url = f"{GRIST_BASE_URL}/tables/{GRIST_TABLE}/records"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    resp.raise_for_status()
    return resp.json().get("records", [])


def build_zone_status(records: list) -> dict:
    zone_status: dict = {}
    for rec in records:
        fields = rec.get("fields", {})
        zone = fields.get("Zone")
        if not zone:
            continue
        zone_status.setdefault(zone, []).append(
            {
                "critere": fields.get("Critere"),
                "station": fields.get("Station"),
                "jours": fields.get("Jours"),
                "seuil": fields.get("Seuil"),
                "cumulActuel": fields.get("CumulActuel"),
                "alerte": bool(fields.get("Alerte")),
                "inactif": bool(fields.get("Inactif")),
                "prog": fields.get("ProgPrelevement"),
            }
        )
    return zone_status


def main() -> None:
    token = os.environ.get("GRIST_BEARER_TOKEN")
    if not token:
        print("Erreur : la variable d'environnement GRIST_BEARER_TOKEN est absente.", file=sys.stderr)
        sys.exit(1)

    records = fetch_records(token)
    zone_status = build_zone_status(records)
    synced_at = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y %H:%M")

    output = {"zoneStatus": zone_status, "syncedAt": synced_at}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")

    nb_alertes = sum(
        1
        for criteres in zone_status.values()
        for c in criteres
        if c["alerte"] and not c["inactif"]
    )
    print(f"OK - {len(zone_status)} zones lues, {nb_alertes} critere(s) actuellement en alerte, syncedAt={synced_at}")


if __name__ == "__main__":
    main()
