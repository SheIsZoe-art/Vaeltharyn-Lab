# Vaeltharyn lexical laboratory

The baseline is frozen at commit `02ad25ebb16e92a5897a54903e1f6a157c2dcbb9`: corpus 1.6.0, plugin/skill 0.8.0, 65,045 entries and 456 expression records. Baseline data, rules and runtime are not rewritten. This is an independent development copy with shared history, not a GitHub-network fork under the same owner.

## Measured inventory

| Resource | Source units | Distinct normalized strings | Lemma/POS matches requiring review |
|---|---:|---:|---:|
| French Morphalou 3.1 | 159,271 lemma records | 144,646 | 51,578 |
| English OEWN 2025 core, excluding Namenet | 135,969 lexical entries | 127,300 | 21,184 |

Wordnet also contains 185,129 word-sense links and 107,519 synsets. Morphalou contains 976,570 inflected-form IDs; these are not counted as Vaeltharyn words. A matching label and part of speech do not establish sense coverage. These totals are neither validated translations nor additions to the canonical dictionary.

36,369 source-linked derivational pairs are available: 7,143 productive-construction leads, 21,560 links to an already matched target and 7,666 further sense analyses. They require review and contain no automatically invented Vaeltharyn spelling.

## Decisions and status

Batch 001 has 130 records: 46 already covered in the selected context, 25 missing aliases, 24 additional senses to distinguish and 35 productive constructions. Categories describe laboratory decisions, not canonical changes. There are 98 written-checked proposals, 12 derived forms awaiting synonym review and 20 unresolved senses without a proposed form. No human or audio validation is claimed.

Reuse a recorded root before inventing another. The twelve prospective derivatives retain their base and stress with licensed `-eth` or `-is`. Sense restrictions, synonyms and register differences stay explicit. Informality in French or English does not establish a Vaeltharyn register. Recorded expressive particles may retain their documented intensity.

`already_covered`: the specified contextual sense is accessible; `missing_alias`: a lookup access point is missing; `additional_sense`: a distinct sense must not overwrite an existing entry; `productive_construction`: a licensed construction; `new_word`: reserved for justified coining, with no new root in this batch. `unresolved_sense` means no form is proposed.

## Query without merging statuses

Baseline lookup remains unchanged. Proposals appear only in a separate `proposals` section with `--proposals`; external entries only with `--source-candidates`. Results are never merged into canonical translations. Inflections are not automatically lemmatized. The review archive does not replace a stable plugin.

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

Editions and hashes are pinned in [the source lock](../../sources/lock.json). Published compressed inventories allow lookup without downloading raw sources. See [licenses](../../LICENSES.md) and [the bilingual batch](batch-001.md). Canonical integration requires an explicit review decision and a new edition; no tool automatically promotes a proposal.
