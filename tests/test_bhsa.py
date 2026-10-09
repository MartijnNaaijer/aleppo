"""The dataset against BHSA 2021: the word mapping, sections, and agreement of the features.

The agreement thresholds are just below the values of version 1.0; a drop means a regression.
"""

import collections
import csv

from aleppo_test_helpers import VERSIFICATION


def mapped(A):
    return [(w, A.F.bhsa.v(w)) for w in A.F.otype.s("word") if A.F.bhsa.v(w)]


def test_mapping_targets_are_bhsa_words(A, B):
    for w, b in mapped(A):
        assert B.F.otype.v(b) == "word"


def test_mapping_keeps_the_order(A):
    targets = [b for _, b in mapped(A)]
    assert all(x <= y for x, y in zip(targets, targets[1:]))


def test_mapping_is_almost_one_to_one(A, B):
    counts = collections.Counter(b for _, b in mapped(A))
    assert sum(1 for n in counts.values() if n > 1) <= 2
    unmapped = [b for b in B.F.otype.s("word") if b not in counts]
    assert len(unmapped) <= 30
    josh = [b for b in unmapped if B.T.sectionFromNode(b)[:2] == ("Joshua", 21)]
    assert len(josh) >= len(unmapped) - 5


def test_reverse_mapping_module(A, B):
    for w, b in mapped(A):
        assert A.F.bhsa.v(B.F.aleppo.v(b)) == b


def test_books_match(A, B):
    for ab, bb in zip(A.F.otype.s("book"), B.F.otype.s("book")):
        assert A.F.book.v(ab) == B.F.book.v(bb)
        assert A.Fs("book@en").v(ab) == B.T.sectionFromNode(bb)[0]


def test_mapped_words_in_the_same_verse_except_known_differences(A, B):
    known = set()
    with open(VERSIFICATION, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            known.add((r["aleppo_book"], int(r["aleppo_chapter"]), int(r["aleppo_verse"])))
    for w, b in mapped(A):
        a_ref, b_ref = A.T.sectionFromNode(w), B.T.sectionFromNode(b)
        assert a_ref == b_ref or a_ref in known, (a_ref, b_ref)


def agreement(A, B, fa, fb, fix=lambda s: s):
    pairs = mapped(A)
    return 100 * sum(A.Fs(fa).v(w) == fix(B.Fs(fb).v(b)) for w, b in pairs) / len(pairs)


def test_agreement_with_bhsa(A, B):
    assert agreement(A, B, "g_cons", "g_cons") >= 99.75
    assert agreement(A, B, "g_cons_utf8", "g_cons_utf8") >= 99.7
    assert agreement(A, B, "trailer_utf8", "trailer_utf8") >= 99.5
    assert agreement(A, B, "g_word_norm", "g_word_utf8") >= 97.9


def test_qere_agreement(A, B):
    pairs = [(w, b) for w, b in mapped(A) if B.F.qere_utf8.v(b)]
    assert sum(A.F.qere_utf8.v(w) is not None for w, b in pairs) >= 1715


def test_genesis_1_1_identical_to_bhsa(A, B):
    ref = ("Genesis", 1, 1)
    assert A.T.text(A.T.nodeFromSection(ref), fmt="text-orig-norm") == B.T.text(B.T.nodeFromSection(ref))
