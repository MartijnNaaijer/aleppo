"""Shared fixtures for the tests of the dataset.

    python -m pytest tests

BHSA 2021 is needed for test_bhsa.py. It is looked for in $BHSA_TF, else in
~/text-fabric-data/github/ETCBC/bhsa/tf/2021 (where Text-Fabric downloads it). Without BHSA those tests
are skipped, unless $REQUIRE_BHSA is set (as on GitHub), then they fail.
"""

import os

import pytest

from aleppo_test_helpers import DATASET, MAPPING_MODULE, bhsa_location


@pytest.fixture(scope="session")
def A():
    """The Aleppo dataset, all features loaded."""
    from tf.fabric import Fabric
    return Fabric(locations=DATASET, silent="deep").loadAll(silent="deep")


@pytest.fixture(scope="session")
def B():
    """BHSA 2021 with the mapping module of this repository (feature aleppo)."""
    from tf.fabric import Fabric
    loc = bhsa_location()
    if loc is None:
        if os.environ.get("REQUIRE_BHSA"):
            pytest.fail("BHSA 2021 not found (set BHSA_TF)")
        pytest.skip("BHSA 2021 not available")
    return Fabric(locations=[loc, MAPPING_MODULE], silent="deep").load(
        "g_word_utf8 g_cons g_cons_utf8 trailer_utf8 qere_utf8 aleppo", silent="deep")
