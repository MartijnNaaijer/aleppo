"""Consistency of the dataset (tf/1.0) on its own."""

import re

import pytest

from aleppo_test_helpers import key

HEBREW_LETTER = re.compile(r"[א-ת]")
TRAILER = re.compile(r"^(|־| |׀ |׃ (ס |פ )?(׆ )?| [ספ] )$")
PAGE = re.compile(r"^(fragment|\d+a?:[ab]( \d+a?:[ab])*)$")


def letters(s):
    return HEBREW_LETTER.findall(s or "")


def words(A):
    return list(A.F.otype.s("word"))


# ------------------------------------------------------------------ structure


def test_node_types_and_sections(A):
    counts = {t: len(A.F.otype.s(t)) for t in ("book", "chapter", "verse", "word")}
    assert counts == dict(book=39, chapter=929, verse=23202, word=426562)
    assert A.F.otype.slotType == "word"
    assert list(A.T.sectionTypes) == ["book", "chapter", "verse"]


def test_text_formats(A):
    assert {"text-orig-full", "text-orig-full-ketiv", "text-orig-norm", "text-orig-norm-ketiv",
            "text-orig-plain", "text-trans-plain"} <= set(A.T.formats)


def test_sections_are_ordered_and_complete(A):
    for b in A.F.otype.s("book"):
        chapters = [A.F.chapter.v(c) for c in A.L.d(b, "chapter")]
        assert chapters == list(range(1, len(chapters) + 1)), A.F.book.v(b)
        for c in A.L.d(b, "chapter"):
            verses = [A.F.verse.v(v) for v in A.L.d(c, "verse")]
            assert verses == sorted(set(verses)) and verses[0] == 1, (A.F.book.v(b), A.F.chapter.v(c))


def test_every_word_in_one_verse(A):
    for w in words(A):
        assert len(A.L.u(w, "verse")) == 1


def test_section_lookup_round_trip(A):
    for v in list(A.F.otype.s("verse"))[::500]:
        assert A.T.nodeFromSection(A.T.sectionFromNode(v)) == v


def test_every_verse_ends_with_sof_pasuq(A):
    for v in A.F.otype.s("verse"):
        last = A.L.d(v, "word")[-1]
        assert "׃" in A.F.trailer_utf8.v(last), A.T.sectionFromNode(v)


# ------------------------------------------------------------------ word features


def test_trailers(A):
    values = {A.F.trailer_utf8.v(w) for w in words(A)}
    assert all(TRAILER.match(t) for t in values), [t for t in values if not TRAILER.match(t)]
    assert all(A.F.trailer.v(w) is not None for w in words(A))


def test_g_cons_matches_the_word(A):
    for w in words(A):
        g, gc = A.F.g_word_utf8.v(w) or "", A.F.g_cons.v(w) or ""
        assert key(g) == gc.replace("_", "").replace("F", "C"), (w, g, gc)
        assert letters(A.F.g_cons_utf8.v(w)) == letters(g), (w, g)


def test_normalization_keeps_letters_and_removes_edition_marks(A):
    for w in words(A):
        g, n = A.F.g_word_utf8.v(w) or "", A.F.g_word_norm.v(w) or ""
        assert letters(n) == letters(g), (w, g, n)
        assert not set(n) & set("͏‍ׇֺﬞ"), (w, n)


def test_qere_features_go_together(A):
    for w in words(A):
        q = A.F.qere_utf8.v(w)
        present = [x is not None for x in (q, A.F.qere_norm.v(w), A.F.qere_cons.v(w), A.F.qere_trailer_utf8.v(w), A.F.kq.v(w))]
        assert all(present) or not any(present), w
        if q is not None:
            assert key(q) == A.F.qere_cons.v(w).replace("_", "").replace("F", "C"), (w, q)
            assert letters(A.F.qere_norm.v(w)) == letters(q)


def test_empty_words(A):
    for w in words(A):
        if not A.F.g_word_utf8.v(w):
            # elided article (no trailer) or qere without ketiv
            assert A.F.trailer_utf8.v(w) == "" or A.F.qere_utf8.v(w), w
            assert not A.F.g_cons.v(w)


def test_mapping_features(A):
    segs = {A.F.bhsa_seg.v(w) for w in words(A)}
    assert segs == {"equal", "aligned", "none"}
    for w in words(A):
        assert (A.F.bhsa.v(w) is None) == (A.F.bhsa_seg.v(w) == "none")


# ------------------------------------------------------------------ verse features


def test_codex_features(A):
    for v in A.F.otype.s("verse"):
        ext, page, photo = A.F.aleppo_extant.v(v), A.F.aleppo_page.v(v), A.F.aleppo_photo.v(v)
        assert ext in (0, 1)
        assert (page is not None) == (ext == 1), A.T.sectionFromNode(v)
        if page:
            assert PAGE.match(page), page
        if photo:
            assert ext == 0


def test_codex_pages_follow_the_text(A):
    """Within a book the pages of the codex follow the order of the verses (checks the parsing of the key).
    The order of the books in the codex differs from the BHSA (e.g. Chronicles before Psalms)."""
    def order(page):
        leaf, side = page.split(":")
        return (int(leaf.rstrip("a")), leaf.endswith("a"), side)

    for b in A.F.otype.s("book"):
        last = None
        for v in A.L.d(b, "verse"):
            page = A.F.aleppo_page.v(v)
            if not page or page == "fragment":
                continue
            pages = [order(p) for p in page.split()]
            assert pages == sorted(pages), A.T.sectionFromNode(v)
            if last is not None:
                assert pages[0] >= last and pages[0][0] - last[0] <= 1, A.T.sectionFromNode(v)
            last = pages[-1]


@pytest.mark.parametrize("ref,extant", [
    (("Genesis", 1, 1), 0), (("Exodus", 8, 17), 1), (("Deuteronomy", 28, 16), 0), (("Deuteronomy", 28, 17), 1),
    (("2_Kings", 14, 21), 1), (("2_Kings", 14, 22), 0), (("2_Kings", 18, 13), 1),
    (("Jeremiah", 32, 14), 1), (("Jeremiah", 32, 15), 0), (("Jeremiah", 32, 19), 1),
    (("Obadiah", 1, 1), 0), (("Micah", 5, 1), 1), (("Haggai", 1, 1), 0), (("Zechariah", 9, 17), 1),
    (("Psalms", 15, 1), 0), (("Psalms", 25, 2), 1), (("Song_of_songs", 3, 11), 1), (("Song_of_songs", 4, 1), 0),
    (("Ecclesiastes", 1, 1), 0), (("2_Chronicles", 1, 1), 1), (("2_Chronicles", 36, 1), 1), (("Ruth", 1, 1), 1),
])
def test_known_lost_and_extant_verses(A, ref, extant):
    assert A.F.aleppo_extant.v(A.T.nodeFromSection(ref)) == extant


def test_double_accentuation_only_where_expected(A):
    # the Decalogue (Exod 20, Deut 5) and Reuben and Bilhah (Gen 35:22)
    refs = {A.T.sectionFromNode(v)[:2] for v in A.F.otype.s("verse") if A.F.accents_alt.v(v)}
    assert refs == {("Exodus", 20), ("Deuteronomy", 5), ("Genesis", 35)}


# ------------------------------------------------------------------ regressions


def test_regression_words_inside_notes(A):
    # the old TSVs lost words inside {{נוסח}}
    assert A.T.text(A.T.nodeFromSection(("Genesis", 1, 1))).startswith("בְּרֵאשִׁ֖ית בָּרָ֣א")
    assert "יְהִ֣י א֑וֹר" in A.T.text(A.T.nodeFromSection(("Genesis", 1, 3)))


def test_regression_qere_without_ketiv(A):
    v = A.T.nodeFromSection(("2_Kings", 19, 31))
    assert "צְבָא֖וֹת" in A.T.text(v) and "צְבָא֖וֹת" not in A.T.text(v, fmt="text-orig-full-ketiv")
