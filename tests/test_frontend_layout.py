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


def test_collapsed_and_mobile_navigation_controls_have_separate_roles():
    source = FRONTEND.read_text(encoding="utf-8")

    assert 'id="sidebar-expand"' in source
    assert ".sidebar-collapsed .sidebar-expand{display:grid" in source
    assert "margin:0 0 10px" in source
    assert 'id="mobile-menu-button"' in source
    assert 'class="sidebar-read-only">Read-only</span>' in source
    assert ".sidebar-footer>.sidebar-read-only" in source
    assert 'new Event("hass-toggle-menu"' in source
    assert ".sidebar-toggle,.sidebar-expand{display:none!important}" in source


def test_dynamic_label_values_are_excluded_from_localization():
    source = FRONTEND.read_text(encoding="utf-8")

    assert 'closest("[data-no-localize]")' in source
    assert (
        '<span data-no-localize>${escapeHtml(item.title)}</span>'
        in source
    )
    assert (
        'Description: <span data-no-localize>${escapeHtml(item.description)}</span>'
        in source
    )


def test_label_names_link_to_filtered_home_assistant_entities():
    source = FRONTEND.read_text(encoding="utf-8")

    assert (
        'const labelEntityLink = item.module === "labels" ? '
        '`/config/entities?sort=name&group=device&label=${encodeURIComponent(item.id)}`'
        in source
    )
    assert 'class="label-entity-link" href="${labelEntityLink}"' in source
    assert 'icon="mdi:devices" aria-hidden="true"' in source


def test_beta_module_overview_options_are_saved_from_settings():
    source = FRONTEND.read_text(encoding="utf-8")

    assert 'name="${module}_include_overview"' in source
    assert '"Entity IDs": "entity_ids"' in source
    assert '"Exposed & Aliases": "exposed"' in source
    assert 'include_in_overview: form.querySelector' in source
