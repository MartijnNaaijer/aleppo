# Aleppo Codex in Text-Fabric

[![tests](https://github.com/MartijnNaaijer/aleppo/actions/workflows/tests.yml/badge.svg)](https://github.com/MartijnNaaijer/aleppo/actions/workflows/tests.yml)

A [Text-Fabric](https://github.com/annotation/text-fabric) dataset of the Hebrew Bible according to the Aleppo Codex, in the edition
[**מקרא על פי המסורה**](https://he.wikisource.org/wiki/מקרא_על_פי_המסורה) on Hebrew Wikisource. It is made for direct comparison with
[BHSA 2021](https://github.com/ETCBC/bhsa): the words are segmented as in the BHSA, the features have the BHSA names and conventions,
and every word is mapped to its BHSA word. This is a [CACCHT](https://github.com/caccht) dataset.

Licence of the text: CC-BY-SA 4.0. Attribution: "מקרא על פי המסורה", he.wikisource.org.

## The dataset

`tf/1.0/`:
- node types `book` (39), `chapter` (929), `verse` (23,202), `word` (426,562; the slot type)
- sections `book`, `chapter`, `verse`, as in the BHSA: `T.nodeFromSection(("Genesis", 1, 1))` works in both datasets

Features of words:

| feature | content |
|---|---|
| `g_word_utf8` | the word as in the edition; a ketiv is unpointed (as in the BHSA) |
| `g_word_norm` | the word in BHSA encoding conventions, comparable with BHSA `g_word_utf8` (see below) |
| `g_cons`, `g_cons_utf8` | consonants of the (ketiv) word, ETCBC transliteration and Hebrew, as in the BHSA |
| `trailer_utf8`, `trailer` | what follows the word (space, maqaf, paseq, sof pasuq, ס/פ), as in the BHSA |
| `qere_utf8`, `qere_norm`, `qere_cons`, `qere_trailer_utf8` | the qere |
| `kq` | kind of ketiv/qere in the edition (`kq`, `kq-em`, `kq-special`, `qere-only`, `ketiv-only`) |
| `note`, `marks` | textual notes of the edition; large, small, suspended and dotted letters, inverted nun |
| `bhsa`, `bhsa_seg` | the corresponding BHSA 2021 word (a BHSA slot) and how it was matched |

Features of verses:

| feature | content |
|---|---|
| `aleppo_extant` | 1 if the verse is (wholly or partly) on a surviving page of the codex, 0 if it is in a lost part (see below) |
| `aleppo_page` | the page(s) of the codex with the verse, as leaf:side (side a = א, b = ב): `72:a`, `71:b 72:a`, `241a:a`; `fragment` for Exod 8:16–18 |
| `aleppo_photo` | for lost verses known from an old photograph: where the photograph was published |
| `accents_alt` | the Decalogue with each accentuation system separately; the text itself has the combined accents, like the codex and the BHSA |

Text formats: `text-orig-full` (default; with the qere, like the BHSA), `text-orig-full-ketiv`, `text-orig-norm`,
`text-orig-norm-ketiv`, `text-orig-plain`, `text-trans-plain`.

### Mapping to the BHSA

- `bhsa` on Aleppo words; the other direction is the module `tf/bhsa-mapping/2021/` with the feature `aleppo` on BHSA words.
- `mapping/aleppo_bhsa_map.tsv`: the same as a table.
- `mapping/versification_differences.tsv`: the 118 verses that are numbered differently (Decalogue, Num 25:19, Josh 21:36–37 absent in
  the edition, 1 Sam 23:29, Jer 30:25).

```python
import os
from tf.fabric import Fabric

A = Fabric(locations="tf/1.0").loadAll()
B = Fabric(locations=[os.path.expanduser("~/text-fabric-data/github/etcbc/bhsa/tf/2021"), "tf/bhsa-mapping/2021"]).load("g_word_utf8 aleppo")

v = A.T.nodeFromSection(("Ruth", 1, 7))
for w in A.L.d(v, "word"):
    b = A.F.bhsa.v(w)
    if b and A.F.g_word_norm.v(w) != B.F.g_word_utf8.v(b):
        print(A.F.g_word_norm.v(w), "|", B.F.g_word_utf8.v(b))
# הָֽיְתָה | הָיְתָה        meteg
# שָּׁ֔מָּה | שָׁ֔מָּה        dagesh
# כַלֹּותֶ֖יהָ | כַלֹּתֶ֖יהָ  plene spelling
```

### `g_word_norm`

`g_word_utf8` is the edition's text, untouched. `g_word_norm` removes differences that are only encoding or editorial convention, so
that what remains are differences between the manuscripts:
- encoding: the order of the marks on a letter; the holam of וֹ on the preceding letter (BHSA `יֹּ֣ום`); qamats qatan → qamats; holam
  haser for vav → holam; accents repeated on the stressed syllable written as in the BHSA (pashta+pashta → qadma+pashta; no second
  telisha, segolta, zarqa); no combining grapheme joiner;
- the edition's conventions (its introduction, chapter 2): sheva with varika (ﬞ) marks a hataf of the codex under a non-guttural →
  hataf patah; the holam the edition adds in YHWH read Adonai → removed; YHWH read Elohim with sheva instead of the edition's
  hataf segol; a bare ketiv gets shin/sin dots as in the BHSA.

For 1:1 mapped words, `g_word_norm` equals BHSA `g_word_utf8` in 97.9% of the words; `g_cons` equals BHSA `g_cons` in 99.8%.

Note: the BHSA itself writes שׁ/שׂ as precomposed characters (U+FB2A, U+FB2B) in 253 places, mostly in the qere. Replace them by
ש + U+05C1/U+05C2 before comparing.

### Lost parts of the codex

About a third of the Aleppo Codex is lost (7,965 of 23,202 verses). In those parts the edition gives the text of closely related Tiberian manuscripts, so
comparisons with the codex itself should be restricted to verses with `aleppo_extant` = 1 (15,237 of 23,202 verses). The pages are
taken from the edition's [key to the codex](https://he.wikisource.org/wiki/ויקיטקסט:מבוא_למקרא_על_פי_המסורה/מפתח_לכתר_ארם_צובה),
which lists the verses on every surviving page side (after J. David Stark's index). Lost:

| lost part | |
|---|---|
| Gen 1:1 – Deut 28:16 | except a small fragment with Exod 8:16–18; Gen 26:34–27:30 and Deut 4:38–6:3 are known from old photographs |
| 2 Kgs 14:22 – 18:12 | |
| Jer 29:10 – 31:34 | |
| Jer 32:15–18 | a torn leaf |
| Amos 8:13 – Mic 4:14 | with Obadiah and Jonah |
| Hag 1:1 – Zech 9:16 | |
| Ps 15:1 – 25:1 | |
| Song 4:1 – end | and Ecclesiastes, Lamentations, Esther, Daniel, Ezra, Nehemiah |

The verses at the edges (Deut 28:17, 2 Kgs 14:21, Jer 29:9, Mic 5:1, Song 3:11, ...) are partly on a surviving page and count as
extant. 2 Chr 35:7–36:19 is on leaf 241a, which was not brought to Israel with the codex but found later in the United States.

```python
lost = [v for v in A.F.otype.s("verse") if not A.F.aleppo_extant.v(v)]
words_in_codex = [w for w in A.F.otype.s("word") if A.F.aleppo_extant.v(A.L.u(w, "verse")[0])]
```

## Caveats

- **Ketiv/qere.** The edition marks 1,213 ketiv/qere instances. In about 150 places where the BHSA has a qere, the edition
  prints the ketiv pointed without a qere (e.g. 2 Sam 1:11 בְגָדָ֖ו).
- **`aleppo_extant`** is at verse level: a verse partly on a surviving page counts as extant. One obvious error in the key is
  corrected: page 222a ends 1 Chronicles and has 2 Chr 1:1–11 (the key has 2 Chr 1:11 only).
- **Mapping.** 30 BHSA words have no Aleppo word (mostly Josh 21:36–37); 1 Aleppo word has no BHSA word (2 Sam 7:22).

## Contents of this repository

```
tf/1.0/                         the dataset
tf/bhsa-mapping/2021/aleppo.tf  module for BHSA 2021: feature aleppo on BHSA words
mapping/                        the word mapping and the versification differences as tables
tests/                          tests of the dataset
```

## Tests

`python -m pytest tests` (needs `text-fabric` and `pytest`) checks the dataset:
- consistency on its own: sections, the features of a word agree with each other (consonants, normalized text,
  qere), allowed values of trailers and codex features, the pages of the codex in order, known lost and extant verses;
- against BHSA 2021: the mapping (order, both directions, same verse except the listed versification differences) and the
  agreement of the features, with thresholds just below the values of this version.

The BHSA tests use `$BHSA_TF` or `~/text-fabric-data/github/ETCBC/bhsa/tf/2021`, and are skipped when BHSA is not there.
On GitHub the tests run after every push to `main`, with BHSA 2021 downloaded by Text-Fabric.

## How it was made

The edition's wikitext (one page per chapter, `<book> <chapter>/טעמים`, downloaded 2026-10-09 via the MediaWiki API) was parsed
with all its templates (ketiv/qere, textual notes, paragraph marks, paseq, the Decalogue's double accentuation, ...); the words were
segmented after BHSA 2021 by aligning the consonants of both texts; then normalized and transliterated, and written with
Text-Fabric's walker. The conversion scripts are not part of this repository.
