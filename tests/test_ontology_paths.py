from pathlib import Path
from sounio.ontology import _default_cache_dir, _default_ontology_home


def test_ontology_paths_use_user_locations(monkeypatch, tmp_path):
    monkeypatch.delenv('SOUNIO_ONTOLOGY_HOME', raising=False)
    monkeypatch.delenv('SOUNIO_ONTOLOGY_CACHE_DIR', raising=False)
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'data'))
    monkeypatch.setenv('XDG_CACHE_HOME', str(tmp_path / 'cache'))
    assert _default_ontology_home() == tmp_path / 'data/sounio/ontology/bundles'
    assert _default_cache_dir() == tmp_path / 'cache/sounio/ontology'


def test_explicit_ontology_locations_take_precedence(monkeypatch, tmp_path):
    monkeypatch.setenv('SOUNIO_ONTOLOGY_HOME', str(tmp_path / 'bundles'))
    monkeypatch.setenv('SOUNIO_ONTOLOGY_CACHE_DIR', str(tmp_path / 'custom-cache'))
    assert _default_ontology_home() == tmp_path / 'bundles'
    assert _default_cache_dir() == tmp_path / 'custom-cache'
