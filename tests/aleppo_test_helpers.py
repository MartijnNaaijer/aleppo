"""Paths and helpers for the tests of the dataset."""

import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(REPO, "tf", "1.0")
MAPPING_MODULE = os.path.join(REPO, "tf", "bhsa-mapping", "2021")
VERSIFICATION = os.path.join(REPO, "mapping", "versification_differences.tsv")

KEY = dict(zip("אבגדהוזחטיכךלמםנןסעפףצץקרשת", ">BGDHWZXVJKKLMMNNS<PPYYQRCT"))


def key(s):
    """Consonants of Hebrew text in ETCBC transliteration, sin and shin both as C."""
    s = (s or "").replace("שׁ", "ש").replace("שׂ", "ש")
    return "".join(KEY[c] for c in s if c in KEY)


def bhsa_location():
    candidates = [os.environ.get("BHSA_TF")] + [
        os.path.expanduser(f"~/text-fabric-data/github/{org}/bhsa/tf/2021") for org in ("ETCBC", "etcbc")]
    for loc in candidates:
        if loc and os.path.exists(os.path.join(loc, "otype.tf")):
            return loc
    return None
