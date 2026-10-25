# Référentiel du laboratoire — schéma 2

Le laboratoire 0.2.0 utilise une seule base Vaeltharyn : les **65 045 entrées** et **456 fiches d’expressions** du corpus stable 1.6.0, figé au commit `02ad25ebb16e92a5897a54903e1f6a157c2dcbb9`. Les sources, règles et installations du plugin/skill 0.8.0 restent inchangées.

## Quatre éléments distincts

| Élément | Emplacement | Rôle |
|---|---|---|
| Base canonique | chemins du manifeste racine `corpus.json` | mots Vaeltharyn, définitions, identifiants stables |
| Inventaires externes | `lab/data/morphalou-lemmas.jsonl.gz`, `oewn-entries.jsonl.gz`, `oewn-synsets.jsonl.gz` | données sources et sens externes, sans liens Vaeltharyn recopiés |
| Correspondances | `lab/data/alignments.jsonl.gz` | table unique des liens source → entrée ou expression canonique, avec portée, statut et preuves |
| Changements proposés | `lab/proposals/batch-001.json` | 84 changements envisagés, sans éléments déjà documentés comme couverts |

Les 46 fiches de contexte existant sont dans `lab/mappings/assessments.json`. Leurs notes qualifient les liens de la table centrale : elles ne créent pas de mots et ne sont pas des changements en attente. Les 130 identifiants de cas d’origine, leurs formulations et leurs réserves sont conservés.

## Sens et statut

La relation compare toujours la **source externe** à la **cible Vaeltharyn** :

- `same_sense` : même sens enregistré ; décision explicite nécessaire.
- `source_broader` : sens source plus large que la cible.
- `source_narrower` : sens source plus étroit que la cible.
- `uncertain` : équivalence non établie, même si un usage contextualisé est documenté.
- `rejected` : correspondance explicitement rejetée.

Le statut précise le travail effectué : `unreviewed`, `written_context_check`, `proposed_change` ou `quarantined_pos`. Tous les liens actuels restent `uncertain` : un contrôle écrit de contexte n’est pas une identité sémantique validée. Les 63 liens en quarantaine ont une catégorie cible trop générale ; ils restent traçables mais sont exclus par défaut des résultats actifs. Une catégorie inconnue n’est jamais traitée comme une catégorie grammaticale commune.

## Comptes mesurés

| Ressource / Resource | Fiches source / Source records | Entrées canoniques avec candidat / Canonical entries with candidate |
|---|---:|---:|
| Morphalou 3.1 — français / French | 159271 | 51200 |
| Wordnet 2025 core — anglais / English | 135969 | 30027 |

Wordnet conserve 185 129 liens mot-sens. La table centrale compte **82 456 liens**, dont **63 en quarantaine**. Les candidats automatiques relient 53 756 identifiants canoniques à au moins une source ; 11 289 restent sans rapprochement automatique. Ces dernières entrées sont conservées et consultables intégralement par identifiant. Ces chiffres mesurent des rapprochements, pas une couverture sémantique validée.

La file de changements contient 25 alias manquants, 24 sens à distinguer et 35 constructions productives. Parmi ces 84 propositions : 52 sont contrôlées à l’écrit, 12 attendent une revue des synonymes et 20 restent sans forme proposée. Les 36 369 pistes dérivationnelles sont une vue générée dans `lab/dist/`, pas des propositions supplémentaires ni un second référentiel.

## Consultation

Les résultats `baseline`, `source_candidates`, `correspondences`, `documented_contexts` et `proposals` restent séparés. `--proposals` ne renvoie que les changements. `--alignments` consulte les liens et les contextes documentés. `entry` donne la fiche canonique complète, même sans correspondance externe. `--include-quarantined` sert à l’audit ; il ne valide aucun lien. Les comptes totaux restent affichés quand la liste est limitée.

```text
python lab/scripts/lab.py report
python lab/scripts/lab.py query --lang en guilt lie --source-candidates
python lab/scripts/lab.py query --lang en affection --alignments
python lab/scripts/lab.py query --lang fr "Je pige." --proposals
python lab/scripts/lab.py entry VX-002edc4764a80a57
python lab/scripts/lab.py entry VX-002edc4764a80a57 --include-quarantined
```

## Reproduction / Rebuild

```text
python lab/scripts/lab.py fetch
python lab/scripts/compare.py
python lab/scripts/families.py
python lab/scripts/check.py
python -m unittest discover -s tests -v
python -m unittest discover -s lab/tests -v
python lab/scripts/lab.py export
```

[Changements proposés](batch-001.md) · [Contextes documentés](contexts.md) · [Sources et licences](../../LICENSES.md). Le ZIP de revue contient la table centrale et les deux ensembles de cas ; la base stable et les inventaires sources sont distribués séparément. Aucun outil ne promeut automatiquement une proposition.
