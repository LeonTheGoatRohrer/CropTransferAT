"""Offline tests for the GEE helpers (no Earth Engine connection needed)."""

import pytest

from croptransfer.gee_extract import antimeridian_tile_prefixes, utm_zone


@pytest.mark.parametrize(
    "lon, zone",
    [(-180.0, 1), (-174.01, 1), (-85.3737, 16), (15.4395, 33), (179.99, 60), (180.0, 60)],
)
def test_utm_zone(lon, zone):
    assert utm_zone(lon) == zone


def test_antimeridian_tiles_dropped_for_project_sites():
    # Graz (zone 33) and KBS (zone 16): both artefact zones are removed.
    assert antimeridian_tile_prefixes(15.4395) == ["T01", "T60"]
    assert antimeridian_tile_prefixes(-85.3737) == ["T01", "T60"]


def test_antimeridian_tiles_kept_for_sites_in_those_zones():
    assert antimeridian_tile_prefixes(-179.0) == ["T60"]
    assert antimeridian_tile_prefixes(178.0) == ["T01"]
