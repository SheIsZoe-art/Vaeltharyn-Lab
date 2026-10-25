# Vaeltharyn Lab · SheIsZoe

**Laboratoire de développement / Development laboratory — 0.1.0**

[Français](lab/docs/fr/README.md) · [English](lab/docs/en/README.md) · [Lot bilingue / Bilingual batch](lab/docs/fr/batch-001.md)

Base figée / Frozen baseline: corpus **1.6.0**, translator **0.8.0**, commit `02ad25ebb16e92a5897a54903e1f6a157c2dcbb9`.

| Élément / Item | Volume |
|---|---:|
| Base Vaeltharyn inchangée / Unchanged baseline | 65 045 entrées / entries |
| Inventaire français / French source lemma records | 159 271 |
| Inventaire anglais / English source lexical entries | 135 969 |
| Sens anglais / English word-sense links | 185 129 |
| Premier lot examiné / First examined batch | 130 fiches / records |
| Relations dérivationnelles à examiner / Derivational pairs to review | 36 369 |

Les inventaires externes ne sont pas des traductions validées. Les propositions sont séparées de la base et visibles uniquement sur demande. / External inventories are not validated translations. Proposals are separate from the baseline and visible only on request.

```text
python lab/scripts/lab.py report
python lab/scripts/lab.py query --lang en guilt whisper --source-candidates
python lab/scripts/lab.py query --lang fr "Je pige." --proposals
```

Python 3.11+, bibliothèque standard uniquement / standard library only.

[Projet stable / Stable project](https://github.com/SheIsZoe-art/Vaeltharyn) · [Sources et licences / Sources and licenses](lab/LICENSES.md) · [Tests](lab/tests/)

Le développement conserve les commits suivants ; aucun historique du laboratoire n’est réécrit pour remplacer une édition. / Development appends commits; laboratory history is not rewritten to replace an edition.
