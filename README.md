# Aleppo Codex in Text-Fabric

A [Text-Fabric](https://github.com/annotation/text-fabric) dataset of the Hebrew Bible according to the Aleppo Codex, in the edition
[**מקרא על פי המסורה**](https://he.wikisource.org/wiki/מקרא_על_פי_המסורה) on Hebrew Wikisource. It is made for direct comparison with
[BHSA 2021](https://github.com/ETCBC/bhsa): the words are segmented as in the BHSA, the features have the BHSA names and conventions,
and every word is mapped to its BHSA word.

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

Features of verses: `aleppo_extant` (0 where the codex is lost and the edition follows related manuscripts) and
`accents_alt` (the Decalogue with each accentuation system separately; the text itself has the combined accents, like the
codex and the BHSA).

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

## Caveats

- **Ketiv/qere.** The edition marks 1,213 ketiv/qere instances. In about 150 places where the BHSA has a qere, the edition
  prints the ketiv pointed without a qere (e.g. 2 Sam 1:11 בְגָדָ֖ו).
- **`aleppo_extant`** follows the edition's list of lacunae at verse level; verses at the edges of a lacuna count as lost.
- **Mapping.** 30 BHSA words have no Aleppo word (mostly Josh 21:36–37); 1 Aleppo word has no BHSA word (2 Sam 7:22).

## Contents of this repository

```
tf/1.0/                         the dataset
tf/bhsa-mapping/2021/aleppo.tf  module for BHSA 2021: feature aleppo on BHSA words
mapping/                        the word mapping and the versification differences as tables
```

## How it was made

The edition's wikitext (one page per chapter, `<book> <chapter>/טעמים`, downloaded 2026-10-09 via the MediaWiki API) was parsed
with all its templates (ketiv/qere, textual notes, paragraph marks, paseq, the Decalogue's double accentuation, ...); the words were
segmented after BHSA 2021 by aligning the consonants of both texts; then normalized and transliterated, and written with
Text-Fabric's walker. The conversion scripts are not part of this repository.
