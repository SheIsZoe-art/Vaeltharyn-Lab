# Vaeltharyn Lab · SheIsZoe

**Laboratoire 0.2.0 / Laboratory 0.2.0 — schéma / schema 2**

[Français](lab/docs/fr/README.md) · [English](lab/docs/en/README.md) · [Changements / Changes](lab/docs/fr/batch-001.md) · [Contextes / Contexts](lab/docs/fr/contexts.md)

| Ensemble / Layer | Volume |
|---|---:|
| Base Vaeltharyn unique et inchangée / Single unchanged baseline | 65 045 entrées / entries |
| Inventaire français Morphalou / French source records | 159 271 |
| Inventaire anglais Wordnet / English source entries | 135 969 |
| Table centrale / Central ledger | 82 456 liens candidats / candidate links |
| Contextes documentés / Documented contexts | 46 |
| Changements proposés / Proposed changes | 84 |
| Liens exclus par défaut / Links excluded by default | 63 |

Base figée / Frozen baseline: corpus **1.6.0**, translator **0.8.0**, commit `02ad25ebb16e92a5897a54903e1f6a157c2dcbb9`.

Les sources externes ne contiennent plus de correspondances Vaeltharyn recopiées. Les liens, leur portée et leur statut ont une table unique. Les propositions restent distinctes des contextes déjà documentés. Aucun rapprochement automatique ne vaut identité de sens.

External inventories no longer mirror Vaeltharyn mappings. Correspondences, scope and status use one ledger. Proposed changes remain separate from documented contexts. Automatic matching does not establish sense identity.

```text
python lab/scripts/lab.py report
python lab/scripts/lab.py query --lang en guilt --source-candidates
python lab/scripts/lab.py query --lang en affection --alignments
python lab/scripts/lab.py query --lang fr "Je pige." --proposals
python lab/scripts/lab.py entry VX-002edc4764a80a57
```

Python 3.11+, bibliothèque standard uniquement / standard library only.

[Projet stable / Stable project](https://github.com/SheIsZoe-art/Vaeltharyn) · [Sources et licences / Licenses](lab/LICENSES.md) · [Téléchargements / Downloads](https://github.com/SheIsZoe-art/Vaeltharyn-Lab/releases/tag/v0.2.0-lab.1)

L’historique progresse par nouveaux commits. La base, le plugin et le skill stables ne sont pas remplacés. / History advances through new commits. The stable baseline, plugin and skill are not replaced.
