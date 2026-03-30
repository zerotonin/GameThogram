from pyvisor.GUI.model.behaviour import Behaviour


def test_to_dict():
    behav = Behaviour(
        animal_number=0,
        color='#FFAA50',
        icon_path='/home/icons/are/nice.png',
        name='aggression',
    )

    d = behav.to_dict()

    assert d['animal'] == 0
    assert d['color'] == '#FFAA50'
    assert d['icon_path'] == '/home/icons/are/nice.png'
    assert d['name'] == 'aggression'
    assert d['compatible_with'] == []
    assert 'key_bindings' in d


def test_from_dict():
    d = {
        'animal': 1,
        'name': 'chill',
        'color': None,
        'icon_path': '/home/icons/are/quite/okay.png',
        'compatible_with': ['swim'],
        'key_bindings': {
            'X-Box': None,
            'Playstation': 'B0',
            'Keyboard': None,
            'Free': None,
        },
    }

    behav = Behaviour.from_dict(d)

    assert behav.animal_number == 1
    assert behav.name == 'chill'
    assert behav.color is None
    assert behav.icon_path == '/home/icons/are/quite/okay.png'
    assert behav.compatible_with == ['swim']
    assert behav.key_bindings['Playstation'] == 'B0'
    assert behav.key_bindings['X-Box'] is None
    assert behav.label == 'A1_chill'


def test_roundtrip():
    """to_dict → from_dict should preserve all fields."""
    original = Behaviour(
        animal_number=2,
        color='#00FF00',
        icon_path='/icons/frog.png',
        name='jump',
        compatible_with=['swim', 'croak'],
    )
    original.key_bindings['X-Box'] = 'B3'
    original.key_bindings['Playstation'] = 'B1'

    restored = Behaviour.from_dict(original.to_dict())

    assert restored.animal_number == original.animal_number
    assert restored.name == original.name
    assert restored.color == original.color
    assert restored.icon_path == original.icon_path
    assert restored.compatible_with == original.compatible_with
    assert restored.key_bindings['X-Box'] == 'B3'
    assert restored.key_bindings['Playstation'] == 'B1'
    assert restored.label == original.label