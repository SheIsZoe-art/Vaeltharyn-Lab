# Laboratory reference model — schema 2

Laboratory 0.2.0 uses one Vaeltharyn baseline: **65,045 entries** and **456 expression records**, corpus 1.6.0 frozen at commit `02ad25ebb16e92a5897a54903e1f6a157c2dcbb9`. Baseline data, rules and installed translator/skill 0.8.0 remain unchanged.

## Four separate elements

| Element | Location | Role |
|---|---|---|
| Canonical baseline | root `corpus.json` paths | Vaeltharyn words, definitions and stable IDs |
| External inventories | `lab/data/morphalou-lemmas.jsonl.gz`, `oewn-entries.jsonl.gz`, `oewn-synsets.jsonl.gz` | source entries and senses without mirrored Vaeltharyn links |
| Correspondences | `lab/data/alignments.jsonl.gz` | one source-to-canonical ledger with scope, status and evidence |
| Proposed changes | `lab/proposals/batch-001.json` | 84 intended changes, excluding already documented contexts |

The 46 existing-context records are in `lab/mappings/assessments.json`. Their notes qualify ledger links: they neither create words nor represent pending changes. All 130 original case IDs, forms and restrictions are retained.

## Relation and status

Relations always compare the **external source** with the **Vaeltharyn target**:

- `same_sense`: same recorded sense; requires an explicit decision.
- `source_broader`: source sense is broader than the target.
- `source_narrower`: source sense is narrower than the target.
- `uncertain`: equivalence is not established, even if a contextual use is documented.
- `rejected`: equivalence has been explicitly rejected.

Statuses describe the review stage: `unreviewed`, `written_context_check`, `proposed_change` or `quarantined_pos`. All current links remain `uncertain`: written context checking does not establish validated sense identity. The 63 quarantined links have an insufficiently specific target category; they remain traceable but are excluded from active results by default. Unknown categories are never treated as one common grammatical category.

## Measured counts

| Ressource / Resource | Fiches source / Source records | Entrées canoniques avec candidat / Canonical entries with candidate |
|---|---:|---:|
| Morphalou 3.1 — français / French | 159271 | 51200 |
| Wordnet 2025 core — anglais / English | 135969 | 30027 |

Wordnet retains 185,129 word-sense links. The central ledger contains **82,456 links**, including **63 quarantined links**. Automatic candidates connect 53,756 canonical IDs with at least one source; 11,289 have no automatic match. These entries remain fully accessible by canonical ID. Counts measure candidate matches, not validated semantic coverage.

The change queue contains 25 missing aliases, 24 additional senses and 35 productive constructions. Of these 84 proposals, 52 have written checks, 12 await synonym review and 20 have no proposed form. The 36,369 derivational leads are a generated view under `lab/dist/`, not additional proposals or a second reference model.

## Queries

`baseline`, `source_candidates`, `correspondences`, `documented_contexts` and `proposals` remain separate. `--proposals` returns only intended changes. `--alignments` consults the ledger and documented contexts. `entry` returns the full canonical record even without an external link. `--include-quarantined` supports auditing, not approval. Full counts remain available when lists are limited.

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

[Proposed changes](batch-001.md) · [Documented contexts](contexts.md) · [Source licenses](../../LICENSES.md). The review ZIP contains the ledger and both case sets; the baseline and raw inventories are distributed separately. No tool automatically promotes a proposal.
