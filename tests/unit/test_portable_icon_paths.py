from pyvisor.resources import icons_root, portable_icon_path, resolve_icon_path


def test_portable_icon_path_relativizes_bundled_icon():
    absolute = str(icons_root() / "game" / "heart.png")
    assert portable_icon_path(absolute) == "game/heart.png"


def test_portable_icon_path_preserves_external_absolute():
    external = "/home/somebody/custom_icons/star.png"
    assert portable_icon_path(external) == external


def test_portable_icon_path_none():
    assert portable_icon_path(None) is None


def test_resolve_icon_path_resolves_relative_to_icons_root():
    resolved = resolve_icon_path("game/heart.png")
    assert resolved == str(icons_root() / "game" / "heart.png")


def test_resolve_icon_path_none():
    assert resolve_icon_path(None) is None


def test_resolve_icon_path_keeps_existing_absolute(tmp_path):
    icon = tmp_path / "custom.png"
    icon.write_bytes(b"fake")
    assert resolve_icon_path(str(icon)) == str(icon)


def test_resolve_icon_path_recovers_foreign_absolute():
    """An absolute path from another machine with an 'icons/' segment
    should resolve against the local icons root if a matching file exists."""
    foreign = "/home/flytracker/PyProject/GameThogram/pyvisor/resources/icons/game/heart.png"
    resolved = resolve_icon_path(foreign)
    expected = str(icons_root() / "game" / "heart.png")
    assert resolved == expected


def test_roundtrip_bundled_icon():
    absolute = str(icons_root() / "game" / "del.png")
    portable = portable_icon_path(absolute)
    assert portable == "game/del.png"
    assert resolve_icon_path(portable) == absolute
