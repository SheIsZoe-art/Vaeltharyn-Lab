# Laboratoire lexical Vaeltharyn

La base est figée au commit `02ad25ebb16e92a5897a54903e1f6a157c2dcbb9` : corpus 1.6.0, plugin/skill 0.8.0, 65 045 entrées et 456 fiches d’expressions. Les données, règles et outils de la base ne sont pas réécrits. Ce dépôt est une copie de développement indépendante avec historique commun, pas un fork GitHub appartenant au même réseau.

## Volumes mesurés

| Ressource | Unités de source | Libellés normalisés distincts | Correspondances libellé + catégorie à examiner |
|---|---:|---:|---:|
| Morphalou 3.1, français | 159 271 fiches de lemmes | 144 646 | 51 578 |
| OEWN 2025, anglais hors Namenet | 135 969 entrées lexicales | 127 300 | 21 184 |

Wordnet contient aussi 185 129 liens mot-sens et 107 519 groupes de sens. Morphalou contient 976 570 identifiants de formes fléchies, qui ne sont pas comptés comme mots Vaeltharyn. Un libellé identique, même avec la même catégorie, ne prouve pas que tous ses sens sont couverts. Ces volumes ne sont donc ni des traductions validées ni des ajouts au dictionnaire.

36 369 relations dérivationnelles reliées à des candidats de la base sont disponibles : 7 143 pistes de construction productive, 21 560 relations vers une forme déjà repérée et 7 666 autres analyses de sens. Elles restent à examiner, sans graphie Vaeltharyn générée automatiquement.

## Statuts et décisions

Le premier lot compte 130 fiches : 46 déjà couvertes dans le contexte retenu, 25 alias manquants, 24 sens supplémentaires à distinguer et 35 constructions productives. Les classes qualifient une décision dans le laboratoire, pas un changement du canon. 98 propositions ont un contrôle écrit de sens/construction, 12 dérivés attendent une revue des synonymes, 20 sens restent sans forme proposée. Aucune validation humaine ou sonore n’est revendiquée.

Une racine existante est réutilisée avant d’en inventer une autre. Les douze formes dérivées candidates conservent leur base et leur accent, avec `-eth` ou `-is` suivant les règles. Les ambiguïtés de sens, synonymes et variantes de registre restent visibles ; un registre familier anglais ou français ne crée pas à lui seul un registre Vaeltharyn. Les particules expressives déjà documentées peuvent être employées avec leur intensité.

`already_covered` : sens décrit déjà accessible dans la base ; `missing_alias` : accès lexical à ajouter ; `additional_sense` : sens distinct à traiter sans détourner une fiche existante ; `productive_construction` : construction selon les règles ; `new_word` : catégorie réservée à une création justifiée, aucune nouvelle racine dans ce lot. `unresolved_sense` signifie qu’aucune forme n’est proposée.

## Consulter sans confondre

La recherche ordinaire de la base est inchangée. Les propositions n’apparaissent que dans la section `proposals` avec `--proposals` ; les données externes, seulement avec `--source-candidates`. Les résultats ne sont jamais fusionnés en traductions canoniques. Les formes fléchies ne sont pas automatiquement lemmatisées. Aucun plugin stable n’est remplacé par l’archive du laboratoire.

```text
python lab/scripts/lab.py report
python lab/scripts/lab.py query --lang en guilt lie whisper --source-candidates
python lab/scripts/lab.py query --lang fr "Je pige." --proposals
python lab/scripts/check.py
python -m unittest discover -s lab/tests -v
python -m unittest discover -s tests -v
python lab/scripts/lab.py export
```

## Reproduire / Reproduce

```text
python lab/scripts/lab.py fetch
python lab/scripts/compare.py
python lab/scripts/families.py
python lab/scripts/check.py
```

Les éditions et empreintes sont figées dans [le catalogue des sources](../../sources/lock.json). Les données compressées publiées évitent les téléchargements pour la consultation. Voir [licences](../../LICENSES.md) et [lot bilingue](batch-001.md). Une intégration au canon nécessite une décision de revue explicite et une nouvelle édition ; aucun outil ne promeut automatiquement une proposition.
