# Licenses and source attribution / Licences et attributions

The baseline Vaeltharyn corpus and original laboratory material retain the terms in [the project license](../LICENSE.md), with creator attribution to **SheIsZoe**. Individual source terms remain applicable. Source datasets are separate resources, not relicensed as a single Vaeltharyn dictionary.

| Files | Resource and attribution | Terms |
|---|---|---|
| `data/morphalou-lemmas.jsonl.gz` | ATILF (CNRS / Université de Lorraine), Morphalou 3.1, ORTOLANG | LGPL-LR; [supplied license](sources/licenses/morphalou-LGPL-LR.txt) |
| `data/oewn-entries.jsonl.gz`, `data/oewn-synsets.jsonl.gz`, `dist/derivation-review.jsonl.gz` (generated view) | Open English Wordnet Team; underlying Princeton University WordNet | CC-BY 4.0 with underlying WordNet notice; [OEWN license](sources/licenses/oewn-license.md), [WordNet notice](sources/licenses/oewn-princeton-license.txt) |
| `proposals/batch-001.json`, `mappings/assessments.json`, `data/alignments.jsonl.gz` | Original Vaeltharyn proposals by SheIsZoe, linked to baseline IDs and OEWN senses | Project terms for original writing; external source attribution retained |

The French inventory is a modified extraction: CSV lemma metadata and source IDs retained; inflected-form rows counted but not reproduced as Vaeltharyn words. OEWN XML is transformed into JSONL, retaining entry, sense and synset identifiers, definitions and relations. Comparison annotations and proposals are added data, kept outside the source inventories in the central ledger and case records. The ledger stores source identifiers and original analysis; original resource licenses remain applicable to the separately distributed source data. No endorsement by source authors is claimed.

Morphalou's mirror metadata has conflicting short license labels; the resource's bundled **LGPL-LR** license and explicit source documentation govern this extraction. Full downloadable source locations, editions and SHA-256 hashes are recorded in [the source lock](sources/lock.json); `python lab/scripts/lab.py fetch` retrieves the source files. Keep this license notice with extracts and exports. Morphalou and Wordnet source data remain replaceable and separately identifiable.

**TLFi is consultation-only here. No TLFi dictionary text or examples are bulk copied or redistributed.** Its publisher describes a closed historical resource with restrictions on reuse. Lexical pages were not consistently readable through automated access; absence of a parsed article is not treated as absence of a sense. The lab also links to selected institutional references without reproducing their texts.

Le référentiel stable conserve ses attributions existantes, notamment celles du Wiktionnaire. Les statuts de proposition et les liens de sens ne constituent pas une validation humaine, une autorisation de réutilisation générale ou une approbation institutionnelle.
