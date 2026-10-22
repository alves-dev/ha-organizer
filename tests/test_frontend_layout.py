from pathlib import Path

FRONTEND = Path(__file__).parents[1] / (
    "custom_components/ha_organizer/frontend/ha-organizer.js"
)


def test_navigation_sidebar_cannot_overflow_horizontally():
    source = FRONTEND.read_text(encoding="utf-8")

    assert ".sidebar{overflow-x:hidden}" in source
    assert ".nav-item>span:not(.nav-beta){min-width:0;overflow:hidden" in source


def test_sidebar_toggle_stays_within_sidebar_bounds():
    source = FRONTEND.read_text(encoding="utf-8")

    assert ".sidebar-toggle{right:8px}" in source


def test_dynamic_label_values_are_excluded_from_localization():
    source = FRONTEND.read_text(encoding="utf-8")

    assert 'closest("[data-no-localize]")' in source
    assert (
        '<strong><span data-no-localize>${escapeHtml(item.title)}</span></strong>'
        in source
    )
    assert (
        'Description: <span data-no-localize>${escapeHtml(item.description)}</span>'
        in source
    )
