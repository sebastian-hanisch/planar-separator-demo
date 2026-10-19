"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und was die Hilfetexte über das Ergebnis behaupten."""

import psp_constants as C
import psp_evaluation as ev
import psp_presets as P


def _analysis(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_bounds():
    for preset in C.PRESETS.values():
        assert preset["net"] in C.NET_TYPES and preset["method"] in C.METHODS
        assert C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["seed"] <= C.SEED_MAX


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Lehrbeispiel: eine Karte"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_textbook_map_has_a_cycle_of_about_sqrt_n_and_a_balanced_split():
    a = _analysis("Lehrbeispiel: eine Karte")
    assert a.sep.method == "cycle" and len(a.sep.vertices) <= 1.1 * a.sqrt_n and a.check.balanced and a.check.largest <= a.check.limit and len(a.sep.vertices) <= a.bound


def test_the_level_preset_is_larger_than_the_cycle_and_above_sqrt_n():
    a = _analysis("Die Schicht ist größer")
    size = len(a.sep.vertices)
    assert a.sep.method == "level" and size > a.others["cycle"] and size > 1.4 * a.sqrt_n


def test_the_median_preset_is_about_sqrt_n():
    a = _analysis("Der Schnitt am Median")
    assert a.sep.method == "geometric" and 0.9 * a.sqrt_n <= len(a.sep.vertices) <= 1.1 * a.sqrt_n


def test_the_lattice_preset_has_a_separator_of_exactly_k_vertices():
    a = _analysis("Gitter: Trennmenge gleich k")
    assert a.inst.n == 144 and len(a.sep.vertices) == 12


def test_the_random_graph_preset_needs_a_fixed_share_of_the_vertices():
    a = _analysis("Zufallsgraph: keine kleine Trennmenge")
    assert not a.inst.planar and 0.12 <= len(a.sep.vertices) / a.inst.n <= 0.25


def test_randomize_seed_stays_inside_the_bounds():
    import streamlit as st

    st.session_state.clear()
    P.randomize_seed()
    assert 0 <= st.session_state["seed_input"] <= C.SEED_MAX
