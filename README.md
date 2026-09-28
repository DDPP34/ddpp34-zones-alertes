# ddpp34-zones-alertes

Petit dépôt public qui republie, une fois par semaine (lundi 06:00 UTC), l'état des zones
de surveillance conchylicole de la DDPP34 (table `Cumuls_Zones_Alertes` du document Grist
"Tableau de saisie_calcul_cumuls_pluvio_DDPP34"), sous la forme d'un fichier `zone-status.json`.

Ce fichier ne contient que des données de suivi non sensibles (codes de zone, critères,
stations, seuils, cumuls, statut d'alerte oui/non) — aucune donnée personnelle, aucun secret.

Il est lu par le tableau de bord REMI/REPHYTOX pour rafraîchir le panneau
"Zones sous surveillance", à l'URL brute GitHub de ce fichier (pas d'API, pas d'authentification
nécessaire côté lecture).

Voir `GUIDE_INSTALLATION.md` (livré séparément) pour la mise en place du secret
`GRIST_BEARER_TOKEN` nécessaire au workflow GitHub Actions.
