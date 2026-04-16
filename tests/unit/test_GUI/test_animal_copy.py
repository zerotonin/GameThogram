from pyvisor.GUI.model.animal import Animal
from pyvisor.GUI.model.behaviour import Behaviour


def _make_source_animal():
    src = Animal(0, "src")
    src[Behaviour(0, name="delete").label] = Behaviour(0, name="delete")
    src[Behaviour(0, name="following").label] = Behaviour(
        0, color="#00aaff", name="following", compatible_with=["licking"]
    )
    src[Behaviour(0, name="licking").label] = Behaviour(
        0, color="#00aaff", name="licking", compatible_with=["following"]
    )
    return src


def test_copy_behaviours_assigns_destination_animal_number():
    src = _make_source_animal()
    dst = Animal(1, "dst")
    dst[Behaviour(1, name="delete").label] = Behaviour(1, name="delete")
    dst.copy_behaviours(src.behaviours)

    for behav in dst.behaviours.values():
        assert behav.animal_number == 1, (
            f"{behav.name} has animal_number={behav.animal_number}, expected 1"
        )
        assert behav.label.startswith("A1_")


def test_copy_behaviours_does_not_share_compatible_with_list():
    src = _make_source_animal()
    dst = Animal(1, "dst")
    dst[Behaviour(1, name="delete").label] = Behaviour(1, name="delete")
    dst.copy_behaviours(src.behaviours)

    src_following = src.behaviours["A0_following"]
    dst_following = dst.behaviours["A1_following"]
    dst_following.compatible_with.append("new_thing")

    assert "new_thing" not in src_following.compatible_with


def test_from_json_dict_coerces_mismatched_animal_number():
    json_dict = {
        "animal_number": 1,
        "animal_name": "LeftMale",
        "behaviours": [
            {
                "animal": 0,
                "name": "following",
                "color": "#ffaa00",
                "icon_path": None,
                "compatible_with": [],
                "key_bindings": {
                    "X-Box": "B3",
                    "Playstation": None,
                    "Keyboard": None,
                    "Free": None,
                },
            },
            {
                "animal": 1,
                "name": "licking",
                "color": "#ffaa00",
                "icon_path": None,
                "compatible_with": [],
                "key_bindings": {
                    "X-Box": "B2",
                    "Playstation": None,
                    "Keyboard": None,
                    "Free": None,
                },
            },
        ],
    }
    animal = Animal.from_json_dict(json_dict)

    for behav in animal.behaviours.values():
        assert behav.animal_number == 1, (
            f"{behav.name} has animal_number={behav.animal_number}, expected 1"
        )
        assert behav.label.startswith("A1_")
