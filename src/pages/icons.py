"""Lightweight inline SVG icon set (Feather-style) used across the SecureRAG UI.

Keeping icons as plain stroke-based SVG (instead of emoji/unicode glyphs)
gives the app a consistent, professional look across platforms and themes.
"""

# Raw SVG path/shape markup for every icon this app uses, keyed by a simple name like "folder" or "trash".
# Each value is just the inner content of an <svg> tag (paths, circles, rects) — icon() below wraps it into a full <svg> element.
_PATHS = {
    "shield": '<path d="M12 2.4 4.4 5.6v6c0 5.3 3.3 9.1 7.6 10.4 4.3-1.3 7.6-5.1 7.6-10.4v-6z"/>',
    "shield-check": '<path d="M12 2.4 4.4 5.6v6c0 5.3 3.3 9.1 7.6 10.4 4.3-1.3 7.6-5.1 7.6-10.4v-6z"/><path d="m9.2 12.1 1.9 1.9 3.7-3.8"/>',
    "lock": '<rect x="3.5" y="10.5" width="17" height="10.5" rx="2.2"/><path d="M7 10.5V7.2a5 5 0 0 1 10 0v3.3"/>',
    "home": '<path d="M3.5 10.2 12 3.4l8.5 6.8V19a1.6 1.6 0 0 1-1.6 1.6H5.1A1.6 1.6 0 0 1 3.5 19z"/><path d="M9.3 20.4v-6.6h5.4v6.6"/>',
    "folder": '<path d="M3.5 6.8a1.7 1.7 0 0 1 1.7-1.7h3.9l1.9 2.1h7.8a1.7 1.7 0 0 1 1.7 1.7v8.4a1.7 1.7 0 0 1-1.7 1.7H5.2a1.7 1.7 0 0 1-1.7-1.7z"/>',
    "message": '<path d="M20.5 11.2a7.9 7.9 0 0 1-7.9 7.9c-1.2 0-2.4-.3-3.4-.8L4 19.5l1.3-4.9a7.8 7.8 0 0 1-.9-3.6 7.9 7.9 0 0 1 7.9-7.9h.3a8 8 0 0 1 7.9 7.9z"/>',
    "user": '<path d="M18.5 20.5v-1.8a3.9 3.9 0 0 0-3.9-3.9H9.4a3.9 3.9 0 0 0-3.9 3.9v1.8"/><circle cx="12" cy="7.8" r="3.6"/>',
    "settings": '<circle cx="12" cy="12" r="2.7"/><path d="M19.4 14.6a1.5 1.5 0 0 0 .3 1.65l.05.05a1.8 1.8 0 1 1-2.55 2.55l-.05-.05a1.5 1.5 0 0 0-1.65-.3 1.5 1.5 0 0 0-.9 1.37V20a1.8 1.8 0 0 1-3.6 0v-.08a1.5 1.5 0 0 0-1-1.4 1.5 1.5 0 0 0-1.65.3l-.05.05a1.8 1.8 0 1 1-2.55-2.55l.05-.05a1.5 1.5 0 0 0 .3-1.65 1.5 1.5 0 0 0-1.37-.9H4a1.8 1.8 0 0 1 0-3.6h.08a1.5 1.5 0 0 0 1.4-1 1.5 1.5 0 0 0-.3-1.65l-.05-.05A1.8 1.8 0 1 1 7.68 4.9l.05.05a1.5 1.5 0 0 0 1.65.3H9.5a1.5 1.5 0 0 0 .9-1.37V3.8a1.8 1.8 0 0 1 3.6 0v.08a1.5 1.5 0 0 0 .9 1.37 1.5 1.5 0 0 0 1.65-.3l.05-.05a1.8 1.8 0 1 1 2.55 2.55l-.05.05a1.5 1.5 0 0 0-.3 1.65v.1a1.5 1.5 0 0 0 1.37.9h.15a1.8 1.8 0 0 1 0 3.6h-.08a1.5 1.5 0 0 0-1.37.9z"/>',
    "logout": '<path d="M9.8 20.5H6.1a1.8 1.8 0 0 1-1.8-1.8V5.3a1.8 1.8 0 0 1 1.8-1.8h3.7"/><path d="m15.5 16.2 4.3-4.2-4.3-4.2"/><path d="M19.6 12H9.6"/>',
    "search": '<circle cx="10.8" cy="10.8" r="6.8"/><path d="m19.9 19.9-4.3-4.3"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.3M12 19.2v2.3M4.6 4.6l1.6 1.6M17.8 17.8l1.6 1.6M2.5 12h2.3M19.2 12h2.3M4.6 19.4l1.6-1.6M17.8 6.2l1.6-1.6"/>',
    "moon": '<path d="M20.2 13.9a8.4 8.4 0 1 1-10.1-10 6.6 6.6 0 0 0 10.1 10z"/>',
    "help": '<circle cx="12" cy="12" r="9.2"/><path d="M9.1 9.3a3 3 0 0 1 5.7 1.2c0 1.9-2.6 2.6-2.7 4.3"/><circle cx="12" cy="17.4" r=".2" fill="currentColor" stroke="none"/>',
    "chevron-down": '<path d="m6 9.5 6 6 6-6"/>',
    "upload": '<path d="M16.3 15.3 12 11l-4.3 4.3"/><path d="M12 11v9.3"/><path d="M20 16.9a4.6 4.6 0 0 0-2.1-8.7h-1.1A7.4 7.4 0 1 0 4 15.2"/>',
    "file": '<path d="M13.5 3H7.2a1.7 1.7 0 0 0-1.7 1.7v14.6A1.7 1.7 0 0 0 7.2 21h9.6a1.7 1.7 0 0 0 1.7-1.7V8.2z"/><path d="M13.2 3v4.9a1 1 0 0 0 1 1H19"/>',
    "check-circle": '<path d="M21 11.1V12a9 9 0 1 1-5.3-8.2"/><path d="m21 4.5-9 9-2.7-2.7"/>',
    "trash": '<path d="M4.5 6.8h15"/><path d="M9.5 6.8V4.9a1.4 1.4 0 0 1 1.4-1.4h2.2a1.4 1.4 0 0 1 1.4 1.4v1.9"/><path d="M6.8 6.8 7.5 19a1.7 1.7 0 0 0 1.7 1.6h5.6a1.7 1.7 0 0 0 1.7-1.6l.7-12.2"/>',
    "filter": '<path d="M4 5.5h16l-6.2 7.3v5.4l-3.6 1.8v-7.2z"/>',
    "documents": '<path d="M14 2.6H6.7A1.7 1.7 0 0 0 5 4.3v15.4a1.7 1.7 0 0 0 1.7 1.7h10.6a1.7 1.7 0 0 0 1.7-1.7V8.3z"/><path d="M13.6 2.6v4.9a1 1 0 0 0 1 1h4.4"/><path d="M8.6 13h6.8M8.6 16.4h6.8"/>',
    "chat": '<path d="M20.5 11.2a7.9 7.9 0 0 1-7.9 7.9c-1.2 0-2.4-.3-3.4-.8L4 19.5l1.3-4.9a7.8 7.8 0 0 1-.9-3.6 7.9 7.9 0 0 1 7.9-7.9h.3a8 8 0 0 1 7.9 7.9z"/>',
    "info": '<circle cx="12" cy="12" r="9.2"/><path d="M12 11v5.6"/><circle cx="12" cy="7.8" r=".25" fill="currentColor" stroke="none"/>',
    "send": '<path d="m4 20 17-8L4 4l2 8-2 8z"/>',
    "chevron-right": '<path d="m9.5 6 6 6-6 6"/>',
    "key": '<circle cx="8" cy="15.5" r="4"/><path d="m11 12.5 8.5-8.5"/><path d="m16.5 6 2.5 2.5"/><path d="m14 8.5 2 2"/>',
    "mail": '<rect x="3.3" y="5.3" width="17.4" height="13.4" rx="1.8"/><path d="m4 6.5 8 6.6 8-6.6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.3l3.6 2.1"/>',
}


# Builds a ready-to-render inline <svg> string for the named icon, at the given pixel size, with an optional extra CSS class.
# If the name isn't in _PATHS, it quietly returns an empty (invisible) svg instead of raising an error.
def icon(name: str, size: int = 16, cls: str = "") -> str:
    body = _PATHS.get(name, "")
    classes = f"icon {cls}".strip()
    return (
        f'<svg class="{classes}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )
