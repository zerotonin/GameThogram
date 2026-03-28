"""Tests for button assignment, stealing, and binding logic.

Covers:
  - Assigning a button to a behaviour
  - Assigning a button to a movie action
  - Stealing a button from one behaviour to another
  - Stealing from a movie action to a behaviour and vice versa
  - Stealing clears ALL duplicates (not just the first)
  - get_action_assigned_to finds the right thing
  - reset_all_bindings clears everything

Run:  pytest tests/test_button_bindings.py -v
"""
import pytest

from pyvisor.GUI.model.animal import Animal
from pyvisor.GUI.model.behaviour import Behaviour
from pyvisor.GUI.model.key_bindings import KeyBindings
from pyvisor.GUI.model.movie_bindings import MovieBindings
from pyvisor.GUI.model.scorer_action import ScorerAction
from pyvisor.GUI.model.gui_data_interface import GUIDataInterface


# ═══════════════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture
def gdi():
    """Create a GUIDataInterface with 2 animals, 2 behaviours each."""
    g = GUIDataInterface()
    g.selected_device = "X-Box"

    # Animal 0
    a0 = Animal(0, "animal_0")
    b0_court = Behaviour(animal_number=0, name="courtship")
    b0_aggr = Behaviour(animal_number=0, name="aggression")
    a0[b0_court.label] = b0_court   # label = "A0_courtship"
    a0[b0_aggr.label] = b0_aggr     # label = "A0_aggression"
    g.animals["animal_0"] = a0

    # Animal 1
    a1 = Animal(1, "animal_1")
    b1_rest = Behaviour(animal_number=1, name="rest")
    b1_loco = Behaviour(animal_number=1, name="locomotion")
    a1[b1_rest.label] = b1_rest     # label = "A1_rest"
    a1[b1_loco.label] = b1_loco     # label = "A1_locomotion"
    g.animals["animal_1"] = a1

    return g


def _assign(gdi, action, button, is_behaviour):
    """Mimic the full assign_button flow: steal, then bind."""
    gdi.steal_button(button)
    gdi.change_button_binding(action, button, is_behaviour)


def _get_behav(gdi, animal_name, label):
    return gdi.animals[animal_name].behaviours[label]


def _get_movie_action(gdi, action_name):
    return gdi.movie_bindings[action_name]


# ═══════════════════════════════════════════════════════════════════
#  Basic assignment
# ═══════════════════════════════════════════════════════════════════

class TestBasicAssignment:
    def test_assign_button_to_behaviour(self, gdi):
        behav = _get_behav(gdi, "animal_0", "A0_courtship")
        _assign(gdi, behav, "B0", is_behaviour=True)
        assert behav.key_bindings["X-Box"] == "B0"

    def test_assign_button_to_movie_action(self, gdi):
        action = _get_movie_action(gdi, "toggleRunMov")
        _assign(gdi, action, "B4", is_behaviour=False)
        assert action.key_bindings["X-Box"] == "B4"

    def test_assign_axis_to_behaviour(self, gdi):
        behav = _get_behav(gdi, "animal_1", "A1_rest")
        _assign(gdi, behav, "A3+", is_behaviour=True)
        assert behav.key_bindings["X-Box"] == "A3+"

    def test_assign_hat_to_behaviour(self, gdi):
        behav = _get_behav(gdi, "animal_0", "A0_aggression")
        _assign(gdi, behav, "H10", is_behaviour=True)
        assert behav.key_bindings["X-Box"] == "H10"

    def test_unassigned_button_returns_none(self, gdi):
        action, is_behav = gdi.get_action_assigned_to("B99")
        assert action is None
        assert is_behav is False


# ═══════════════════════════════════════════════════════════════════
#  Lookup
# ═══════════════════════════════════════════════════════════════════

class TestGetActionAssignedTo:
    def test_find_behaviour(self, gdi):
        behav = _get_behav(gdi, "animal_0", "A0_courtship")
        _assign(gdi, behav, "B0", is_behaviour=True)

        found, is_behav = gdi.get_action_assigned_to("B0")
        assert found is behav
        assert is_behav is True

    def test_find_movie_action(self, gdi):
        action = _get_movie_action(gdi, "toggleRunMov")
        _assign(gdi, action, "B4", is_behaviour=False)

        found, is_behav = gdi.get_action_assigned_to("B4")
        assert found is action
        assert is_behav is False

    def test_returns_none_for_unassigned(self, gdi):
        found, is_behav = gdi.get_action_assigned_to("B77")
        assert found is None
        assert is_behav is False


# ═══════════════════════════════════════════════════════════════════
#  Stealing buttons
# ═══════════════════════════════════════════════════════════════════

class TestStealButton:
    def test_steal_from_behaviour_to_behaviour(self, gdi):
        """Assigning B0 to aggression should clear it from courtship."""
        court = _get_behav(gdi, "animal_0", "A0_courtship")
        aggr = _get_behav(gdi, "animal_0", "A0_aggression")

        _assign(gdi, court, "B0", is_behaviour=True)
        assert court.key_bindings["X-Box"] == "B0"

        _assign(gdi, aggr, "B0", is_behaviour=True)
        assert aggr.key_bindings["X-Box"] == "B0"
        assert court.key_bindings["X-Box"] is None  # stolen

    def test_steal_from_movie_to_behaviour(self, gdi):
        """Assigning B4 to a behaviour should clear it from the movie action."""
        action = _get_movie_action(gdi, "toggleRunMov")
        behav = _get_behav(gdi, "animal_1", "A1_rest")

        _assign(gdi, action, "B4", is_behaviour=False)
        assert action.key_bindings["X-Box"] == "B4"

        _assign(gdi, behav, "B4", is_behaviour=True)
        assert behav.key_bindings["X-Box"] == "B4"
        assert action.key_bindings["X-Box"] is None  # stolen

    def test_steal_from_behaviour_to_movie(self, gdi):
        """Assigning B2 to a movie action should clear it from the behaviour."""
        behav = _get_behav(gdi, "animal_0", "A0_courtship")
        action = _get_movie_action(gdi, "stopToggle")

        _assign(gdi, behav, "B2", is_behaviour=True)
        assert behav.key_bindings["X-Box"] == "B2"

        _assign(gdi, action, "B2", is_behaviour=False)
        assert action.key_bindings["X-Box"] == "B2"
        assert behav.key_bindings["X-Box"] is None  # stolen

    def test_steal_across_animals(self, gdi):
        """Assigning B1 to animal_1 behaviour should clear it from animal_0."""
        b0 = _get_behav(gdi, "animal_0", "A0_aggression")
        b1 = _get_behav(gdi, "animal_1", "A1_locomotion")

        _assign(gdi, b0, "B1", is_behaviour=True)
        assert b0.key_bindings["X-Box"] == "B1"

        _assign(gdi, b1, "B1", is_behaviour=True)
        assert b1.key_bindings["X-Box"] == "B1"
        assert b0.key_bindings["X-Box"] is None  # stolen

    def test_steal_clears_all_duplicates(self, gdi):
        """If multiple actions somehow have the same button, steal clears ALL."""
        b0 = _get_behav(gdi, "animal_0", "A0_courtship")
        b1 = _get_behav(gdi, "animal_1", "A1_rest")
        action = _get_movie_action(gdi, "toggleRunMov")

        # Force duplicates by writing directly (simulating corrupt state)
        b0.key_bindings["X-Box"] = "B5"
        b1.key_bindings["X-Box"] = "B5"
        action.key_bindings["X-Box"] = "B5"

        target = _get_behav(gdi, "animal_0", "A0_aggression")
        _assign(gdi, target, "B5", is_behaviour=True)

        assert target.key_bindings["X-Box"] == "B5"
        assert b0.key_bindings["X-Box"] is None
        assert b1.key_bindings["X-Box"] is None
        assert action.key_bindings["X-Box"] is None

    def test_reassign_same_action_same_button(self, gdi):
        """Reassigning the same button to the same action is a no-op."""
        behav = _get_behav(gdi, "animal_0", "A0_courtship")
        _assign(gdi, behav, "B0", is_behaviour=True)
        _assign(gdi, behav, "B0", is_behaviour=True)
        assert behav.key_bindings["X-Box"] == "B0"

    def test_reassign_action_to_new_button(self, gdi):
        """Changing an action from B0 to B1 should clear B0."""
        behav = _get_behav(gdi, "animal_0", "A0_courtship")
        _assign(gdi, behav, "B0", is_behaviour=True)
        _assign(gdi, behav, "B1", is_behaviour=True)
        assert behav.key_bindings["X-Box"] == "B1"
        # B0 is now free
        found, _ = gdi.get_action_assigned_to("B0")
        assert found is None


# ═══════════════════════════════════════════════════════════════════
#  Movie bindings
# ═══════════════════════════════════════════════════════════════════

class TestMovieBindings:
    def test_get_action_assigned_to_returns_first(self, gdi):
        action = _get_movie_action(gdi, "runMovForward")
        _assign(gdi, action, "A0+", is_behaviour=False)

        found = gdi.movie_bindings.get_action_assigned_to("X-Box", "A0+")
        assert found is action

    def test_get_action_assigned_to_returns_none(self, gdi):
        found = gdi.movie_bindings.get_action_assigned_to("X-Box", "B99")
        assert found is None

    def test_duplicate_movie_bindings_both_cleared_by_steal(self, gdi):
        """Two movie actions with the same button — steal clears both."""
        a1 = _get_movie_action(gdi, "runMovForward")
        a2 = _get_movie_action(gdi, "runMovReverse")

        # Force duplicates
        a1.key_bindings["X-Box"] = "A3-"
        a2.key_bindings["X-Box"] = "A3-"

        target = _get_movie_action(gdi, "toggleRunMov")
        _assign(gdi, target, "A3-", is_behaviour=False)

        assert target.key_bindings["X-Box"] == "A3-"
        assert a1.key_bindings["X-Box"] is None
        assert a2.key_bindings["X-Box"] is None


# ═══════════════════════════════════════════════════════════════════
#  Reset
# ═══════════════════════════════════════════════════════════════════

class TestResetBindings:
    def test_reset_clears_all(self, gdi):
        """reset_all_bindings should leave every binding as None."""
        # Assign everything
        for i, behav in enumerate(
            list(gdi.animals["animal_0"].behaviours.values()) +
            list(gdi.animals["animal_1"].behaviours.values())
        ):
            _assign(gdi, behav, f"B{i}", is_behaviour=True)

        _assign(gdi, _get_movie_action(gdi, "toggleRunMov"), "B10", False)

        gdi.reset_all_bindings()

        for animal in gdi.animals.values():
            for behav in animal.behaviours.values():
                assert behav.key_bindings["X-Box"] is None

        for name in gdi.movie_bindings.keys():
            assert gdi.movie_bindings[name].key_bindings["X-Box"] is None


# ═══════════════════════════════════════════════════════════════════
#  Device categories
# ═══════════════════════════════════════════════════════════════════

class TestDeviceIsolation:
    def test_xbox_binding_does_not_affect_playstation(self, gdi):
        """Bindings on X-Box should not touch Playstation slots."""
        behav = _get_behav(gdi, "animal_0", "A0_courtship")
        gdi.selected_device = "X-Box"
        _assign(gdi, behav, "B0", is_behaviour=True)

        assert behav.key_bindings["X-Box"] == "B0"
        assert behav.key_bindings["Playstation"] is None

    def test_steal_only_affects_current_device(self, gdi):
        """Stealing on X-Box should not clear Playstation bindings."""
        behav = _get_behav(gdi, "animal_0", "A0_courtship")

        # Assign on Playstation
        gdi.selected_device = "Playstation"
        _assign(gdi, behav, "B0", is_behaviour=True)

        # Steal on X-Box
        gdi.selected_device = "X-Box"
        other = _get_behav(gdi, "animal_0", "A0_aggression")
        _assign(gdi, other, "B0", is_behaviour=True)

        # Playstation binding untouched
        assert behav.key_bindings["Playstation"] == "B0"
        assert other.key_bindings["X-Box"] == "B0"
