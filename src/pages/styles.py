import streamlit as st


# Injects one big <style> block with all of the app's CSS, picking either the "dark" or "light" color palette.
# The CSS below uses Python's %-string formatting to drop in each palette color (e.g. %(app)s), so every literal
# "%" that belongs to the CSS itself (like widths or transforms) has to be doubled up as "%%" to survive that formatting.
def load_styles(theme: str = "dark"):
    # The two color palettes this app supports. Every named color here becomes a CSS variable (--app, --surface, etc.)
    # further down, so the rest of the stylesheet never hardcodes a color directly.
    palettes = {
        "dark": {
            "app": "#0a0e18",
            "surface": "#111726",
            "surface2": "#161d2e",
            "side": "#0b0f1a",
            "border": "#212a3d",
            "border_strong": "#2b3550",
            "text": "#f3f6fb",
            "muted": "#93a1b8",
            "subtle": "#67748c",
            "accent": "#3b6bf5",
            "accent_strong": "#2f5eea",
            "soft": "rgba(59,107,245,.15)",
            "success": "#22c55e",
            "success_soft": "rgba(34,197,94,.14)",
            "danger": "#ef4444",
            "danger_soft": "rgba(239,68,68,.14)",
            "input": "#0d1220",
            "shadow": "rgba(2,6,23,.35)",
        },
        "light": {
            "app": "#f5f7fb",
            "surface": "#ffffff",
            "surface2": "#f3f6fb",
            "side": "#ffffff",
            "border": "#e4e9f2",
            "border_strong": "#d3dbe9",
            "text": "#101828",
            "muted": "#5b6b83",
            "subtle": "#7c8aa0",
            "accent": "#3358e0",
            "accent_strong": "#2846c4",
            "soft": "rgba(51,88,224,.10)",
            "success": "#16a34a",
            "success_soft": "rgba(22,163,74,.10)",
            "danger": "#dc2626",
            "danger_soft": "rgba(220,38,38,.09)",
            "input": "#ffffff",
            "shadow": "rgba(16,24,40,.07)",
        },
    }
    p = palettes[theme]
    st.markdown(
        """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --app: %(app)s;
  --surface: %(surface)s;
  --surface2: %(surface2)s;
  --side: %(side)s;
  --border: %(border)s;
  --border-strong: %(border_strong)s;
  --text: %(text)s;
  --muted: %(muted)s;
  --subtle: %(subtle)s;
  --accent: %(accent)s;
  --accent-strong: %(accent_strong)s;
  --soft: %(soft)s;
  --success: %(success)s;
  --success-soft: %(success_soft)s;
  --danger: %(danger)s;
  --danger-soft: %(danger_soft)s;
  --input: %(input)s;
  --shadow: %(shadow)s;
}

/* Base: global font, app background, and small resets applied everywhere. */

html,
body,
[class*="css"] {
  font-family: 'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}

.stApp {
  background: var(--app);
  color: var(--text);
}

header[data-testid="stHeader"] {
  background: var(--app);
}

#MainMenu,
footer {
  visibility: hidden;
}

.block-container {
  max-width: 1500px;
  padding: 4.4rem 1.75rem 2rem !important;
}

::selection {
  background: var(--soft);
}

.icon {
  display: inline-block;
  vertical-align: -3px;
  flex-shrink: 0;
}

a {
  color: var(--accent);
}

/* Sidebar: the left navigation panel, its brand header, user card, nav buttons, and footer note. */

[data-testid="stSidebar"] {
  background: var(--side) !important;
  border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebarHeader"] {
  height: auto !important;
  min-height: 0 !important;
  padding: .5rem .5rem 0 !important;
}

[data-testid="stSidebarCollapseButton"] {
  border-radius: 7px;
}

[data-testid="stSidebarCollapseButton"] button {
  border-radius: 7px !important;
  transition: background .15s ease !important;
}

[data-testid="stSidebarCollapseButton"] button:hover {
  background: var(--surface2) !important;
}

[data-testid="stSidebarCollapseButton"] span {
  color: var(--subtle) !important;
}

[data-testid="stExpandSidebarButton"] {
  top: .6rem !important;
  left: .6rem !important;
}

[data-testid="stExpandSidebarButton"] button {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px var(--shadow) !important;
}

[data-testid="stExpandSidebarButton"] button:hover {
  background: var(--surface2) !important;
}

[data-testid="stExpandSidebarButton"] span {
  color: var(--muted) !important;
}

[data-testid="stSidebarContent"] {
  padding: .4rem 1rem 1rem !important;
  display: flex;
  flex-direction: column;
  min-height: 100%%;
  overflow-y: auto !important;
  scrollbar-width: none !important;
}

[data-testid="stSidebarContent"]::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
}

[data-testid="stSidebarContent"]>[data-testid="stVerticalBlock"] {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  gap: .35rem !important;
}

[data-testid="stSidebarContent"] [data-testid="stVerticalBlock"]>div:has(>.sidebar-spacer) {
  flex: 1 1 auto;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
  color: var(--muted) !important;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: .6rem;
  padding: .2rem .1rem .9rem;
}

.brand-icon {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: linear-gradient(150deg,var(--accent),var(--accent-strong));
  color: #fff;
  box-shadow: 0 4px 14px rgba(59,107,245,.35);
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.18;
}

.brand-title {
  color: var(--text);
  font-size: 1.03rem;
  font-weight: 800;
  letter-spacing: -.02em;
  white-space: nowrap;
}

.brand-subtitle {
  color: var(--subtle);
  font-size: .66rem;
  margin-top: .1rem;
}

.sidebar-user-card {
  display: flex;
  align-items: center;
  gap: .65rem;
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 11px;
  padding: .55rem .7rem;
  margin: 0 0 .8rem;
}

.avatar {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  min-width: 34px;
  border-radius: 50%%;
  background: linear-gradient(150deg,var(--accent),var(--accent-strong));
  color: #fff;
  font-size: .86rem;
  font-weight: 700;
  letter-spacing: 0;
}

.avatar.sm {
  width: 26px;
  height: 26px;
  min-width: 26px;
  font-size: .68rem;
}

.user-name {
  color: var(--text);
  font-size: .85rem;
  font-weight: 700;
  line-height: 1.25;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 11.5rem;
}

.user-id {
  color: var(--subtle);
  font-size: .68rem;
  margin-top: .08rem;
  font-weight: 600;
}

.sidebar-divider {
  height: 1px;
  background: var(--border);
  margin: .3rem .1rem .55rem;
}

.sidebar-nav-label {
  color: var(--subtle);
  font-size: .66rem;
  font-weight: 700;
  letter-spacing: .07em;
  text-transform: uppercase;
  margin: 0 .25rem .45rem;
}

[data-testid="stSidebar"] .stButton>button {
  min-height: 2.35rem;
  justify-content: flex-start;
  flex-wrap: nowrap;
  gap: .6rem;
  background: transparent;
  color: var(--muted) !important;
  border: 1px solid transparent !important;
  border-radius: 9px !important;
  box-shadow: none !important;
  font-weight: 600 !important;
  font-size: .82rem !important;
  white-space: nowrap !important;
  transition: background .15s ease,color .15s ease,box-shadow .15s ease !important;
}

[data-testid="stSidebar"] .stButton>button p {
  font-size: .82rem !important;
  font-weight: 600 !important;
  white-space: nowrap !important;
  color: var(--muted) !important;
}

[data-testid="stSidebar"] .stButton>button svg {
  opacity: .85;
}

[data-testid="stSidebar"] .stButton>button:hover {
  background: var(--surface2) !important;
  color: var(--text) !important;
  transform: none;
  box-shadow: 0 1px 0 var(--border) !important;
}

[data-testid="stSidebar"] .stButton>button:hover p {
  color: var(--text) !important;
}

[data-testid="stSidebar"] button[kind^="primary"] {
  background: var(--soft) !important;
  color: var(--accent) !important;
  border-color: rgba(59,107,245,.28) !important;
  box-shadow: 0 3px 10px rgba(59,107,245,.16) !important;
}

[data-testid="stSidebar"] button[kind^="primary"] p {
  color: var(--accent) !important;
}

[data-testid="stSidebar"] button[kind^="primary"]:hover {
  background: var(--soft) !important;
}

[data-testid="stSidebar"] button[kind^="primary"] svg {
  color: var(--accent) !important;
  opacity: 1;
}

.sidebar-spacer {
  flex: 1;
  min-height: .4rem;
}

.sidebar-footer-card {
  display: flex;
  gap: .55rem;
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 11px;
  padding: .7rem .75rem;
  margin-top: .7rem;
}

.sidebar-footer-card .icon {
  color: var(--success);
  margin-top: .1rem;
}

.sidebar-footer-card .footer-title {
  color: var(--text);
  font-size: .75rem;
  font-weight: 700;
}

.sidebar-footer-card .footer-text {
  color: var(--subtle);
  font-size: .68rem;
  line-height: 1.45;
  margin-top: .15rem;
}

/* Top navbar: the search bar, workspace-isolated status pill, and light/dark theme toggle at the top of the page. */

.st-key-navbar_row [data-testid="stHorizontalBlock"] {
  flex-wrap: nowrap !important;
  gap: .6rem !important;
  align-items: stretch !important;
}

.st-key-navbar_row [data-testid="stHorizontalBlock"]>div[data-testid="stColumn"] {
  min-width: 0 !important;
  width: auto !important;
  height: 2.55rem !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
}

.st-key-navbar_row [data-testid="stHorizontalBlock"]>div:nth-child(1) {
  flex: 0 1 50%% !important;
}

.st-key-navbar_row [data-testid="stHorizontalBlock"]>div:nth-child(2) {
  flex: 1 1 auto !important;
}

.st-key-navbar_row [data-testid="stHorizontalBlock"]>div:nth-child(3),
.st-key-navbar_row [data-testid="stHorizontalBlock"]>div:nth-child(4) {
  flex: 0 0 auto !important;
}

.st-key-navbar_row [data-testid="stHorizontalBlock"]>div [data-testid="stVerticalBlockBorderWrapper"],
.st-key-navbar_row [data-testid="stHorizontalBlock"]>div [data-testid="stVerticalBlock"] {
  justify-content: center !important;
}

.st-key-navbar_row [data-testid="stHorizontalBlock"]>div [data-testid="stElementContainer"] {
  height: 2.55rem !important;
  display: flex !important;
  align-items: stretch !important;
}

.st-key-navbar_row [data-testid="stHorizontalBlock"]>div [data-testid="stElementContainer"] [data-testid="stMarkdown"],
.st-key-navbar_row [data-testid="stHorizontalBlock"]>div [data-testid="stElementContainer"] [data-testid="stMarkdown"]>div,
.st-key-navbar_row [data-testid="stHorizontalBlock"]>div [data-testid="stMarkdownContainer"] {
  display: flex !important;
  align-items: stretch !important;
  height: 100%% !important;
}

.status-pill {
  box-sizing: border-box;
  height: 2.55rem;
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  color: var(--success);
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 999px;
  padding: 0 .85rem 0 .7rem;
  font-size: .76rem;
  font-weight: 650;
  white-space: nowrap;
}

.status-pill .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%%;
  background: var(--success);
  box-shadow: 0 0 0 3px var(--success-soft);
}

.st-key-global_search {
  position: relative;
  width: 100%%;
}

.st-key-global_search [data-testid="stTextInput"] {
  width: 100%% !important;
}

.st-key-global_search [data-testid="stTextInput"] div {
  width: 100%% !important;
}

.st-key-global_search [data-testid="stTextInput"] input {
  width: 100%% !important;
  box-sizing: border-box !important;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important;
  padding: .62rem .9rem .62rem 2.35rem !important;
  font-size: .82rem !important;
  color: var(--text) !important;
  min-height: 2.55rem !important;
}

.st-key-global_search [data-testid="stTextInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--soft) !important;
}

.st-key-global_search [data-testid="stTextInput"] input::placeholder {
  color: var(--subtle) !important;
}

.st-key-global_search::before {
  content: "";
  position: absolute;
  left: .9rem;
  top: 50%%;
  width: 15px;
  height: 15px;
  transform: translateY(-50%%);
  pointer-events: none;
  z-index: 2;
  background: var(--subtle);
  -webkit-mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="10.8" cy="10.8" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>') center/contain no-repeat;
  mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="10.8" cy="10.8" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>') center/contain no-repeat;
}

.search-group-label {
  color: var(--subtle);
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .05em;
  margin: .3rem .1rem .4rem;
}

.search-empty {
  display: flex;
  align-items: center;
  gap: .55rem;
  color: var(--muted);
  font-size: .82rem;
  padding: .3rem .1rem;
}

.search-empty .icon {
  color: var(--subtle);
}

.st-key-theme_toggle [data-testid="stButtonGroup"] button {
  min-width: 2.35rem;
  padding: 0 .5rem !important;
}

/* Auth pages: the centered branding block and footnote link on the login/register screens. */

.auth-brand {
  text-align: center;
  padding: 1.4rem 0 .8rem;
}

.auth-brand-icon {
  display: inline-grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(150deg,var(--accent),var(--accent-strong));
  color: #fff;
  margin-bottom: .85rem;
  box-shadow: 0 8px 20px rgba(59,107,245,.32);
}

.auth-brand h1 {
  font-size: 1.7rem;
  font-weight: 800;
  color: var(--text);
  margin: 0 0 .35rem;
  letter-spacing: -.02em;
}

.auth-brand p {
  color: var(--muted);
  font-size: .82rem;
  margin: 0;
}

.auth-footnote {
  text-align: center;
  color: var(--muted);
  font-size: .78rem;
}

/* Headers: page titles/captions, info cards, and small badge pills reused across most pages. */

.dashboard-header {
  padding: .1rem 0 .9rem;
  margin-bottom: .3rem;
}

.header-name {
  color: var(--text);
  font-size: 1.45rem;
  font-weight: 800;
  letter-spacing: -.03em;
}

.name-accent {
  color: var(--accent);
}

.header-meta {
  display: flex;
  align-items: center;
  gap: .6rem;
  margin-top: .4rem;
  color: var(--muted);
  font-size: .75rem;
}

.header-badge {
  color: var(--text);
  font-weight: 700;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: .08rem .45rem;
}

.page-header {
  display: flex;
  align-items: center;
  gap: .65rem;
  padding: .1rem 0 .35rem;
}

.page-header .icon-badge {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--soft);
  color: var(--accent);
}

.page-header-text {
  display: flex;
  flex-direction: column;
}

.page-title {
  color: var(--text);
  font-size: 1.28rem;
  font-weight: 800;
  letter-spacing: -.02em;
}

.page-caption {
  color: var(--muted);
  font-size: .8rem;
  margin-top: .12rem;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: .5rem;
  color: var(--text);
  font-size: .92rem;
  font-weight: 700;
  margin: .2rem 0 .8rem;
}

.section-heading .icon {
  color: var(--accent);
}

.info-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.1rem;
  box-shadow: 0 2px 10px var(--shadow);
}

.info-card .info-title {
  font-weight: 700;
  color: var(--text);
  font-size: .92rem;
  margin-bottom: .55rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .5rem;
}

.info-card .info-body {
  font-size: .79rem;
  color: var(--muted);
  line-height: 1.7;
}

.info-row {
  display: flex;
  align-items: center;
  gap: .5rem;
  font-size: .79rem;
  color: var(--muted);
  margin-bottom: .5rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .icon {
  color: var(--subtle);
}

.info-row strong {
  color: var(--text);
  font-weight: 650;
}

.badge-pill {
  display: inline-flex;
  align-items: center;
  gap: .3rem;
  font-size: .68rem;
  font-weight: 700;
  padding: .2rem .55rem;
  border-radius: 999px;
}

.badge-pill.success {
  color: var(--success);
  background: var(--success-soft);
  border: 1px solid rgba(34,197,94,.28);
}

/* Stat cards: the small metric tiles at the top of the dashboard (document count, chat count, etc.). */

.stat-card {
  height: 100%%;
  min-height: 112px;
  box-sizing: border-box;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.1rem;
  box-shadow: 0 2px 10px var(--shadow);
  transition: border-color .15s ease;
}

.stat-card:hover {
  border-color: var(--border-strong);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: .6rem;
}

.stat-icon {
  display: inline-grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: var(--soft);
  color: var(--accent);
}

.stat-icon.success {
  background: var(--success-soft);
  color: var(--success);
}

.stat-label {
  color: var(--muted);
  font-size: .76rem;
  font-weight: 650;
}

.stat-value {
  color: var(--text);
  font-size: 1.6rem;
  font-weight: 800;
  margin-top: .7rem;
  letter-spacing: -.03em;
}

.stat-value.success {
  color: var(--success);
}

.stat-subtitle {
  color: var(--subtle);
  font-size: .72rem;
  margin-top: .3rem;
}

/* Panels: the bordered content boxes (like the dashboard's document list and assistant panel). */

.panel-heading {
  color: var(--text);
  font-size: 1.05rem;
  font-weight: 750;
  margin: 0;
  display: flex;
  align-items: center;
  gap: .45rem;
}

.panel-heading .icon {
  color: var(--accent);
}

.panel-caption {
  color: var(--muted);
  font-size: .79rem;
  margin: .3rem 0 1rem;
}

[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--surface);
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 22px var(--shadow);
}

[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
  gap: .45rem;
}

/* Uploader: the drag-and-drop file upload box styling. */

[data-testid="stFileUploader"] {
  background: var(--surface2);
  border: 1.5px dashed var(--border-strong);
  border-radius: 10px;
  padding: .2rem .72rem;
}

[data-testid="stFileUploader"] section {
  padding: 1.15rem .4rem !important;
  min-height: 74px;
  background: transparent !important;
}

[data-testid="stFileUploaderDropzone"] button {
  border-radius: 7px !important;
}

/* Buttons / inputs: shared styling for every button, text input, textarea, and select dropdown in the app. */

.stButton>button {
  border-radius: 8px !important;
  font-weight: 650 !important;
  font-size: .83rem !important;
  min-height: 2.5rem;
  transition: .15s ease !important;
}

button[kind^="primary"] {
  background: var(--accent) !important;
  border: 1px solid var(--accent-strong) !important;
  color: #fff !important;
  box-shadow: 0 6px 16px rgba(59,107,245,.28) !important;
}

button[kind^="primary"]:hover {
  background: var(--accent-strong) !important;
  transform: translateY(-1px);
}

button[kind^="secondary"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
}

button[kind^="secondary"]:hover {
  border-color: var(--border-strong) !important;
}

.process-button {
  margin: .5rem 0 .55rem;
}

.process-button [data-testid="stButton"] button {
  min-height: 2.7rem;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: var(--input) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 8px !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--soft) !important;
}

[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextArea"] [data-baseweb]:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--soft) !important;
}

[data-testid="stTextInput"]:has(button) [data-testid="InputInstructions"] {
  right: 44px !important;
}

[data-testid="stSelectbox"] .react-aria-ComboBox>div {
  background: var(--input) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  min-height: 42px !important;
}

[data-testid="stSelectbox"] .react-aria-ComboBox input {
  color: var(--text) !important;
  font-size: .81rem !important;
  background: transparent !important;
}

[data-testid="stSelectbox"] .react-aria-ComboBox input::placeholder {
  color: var(--subtle) !important;
}

[data-testid="stSelectbox"] .react-aria-ComboBox button svg {
  color: var(--subtle) !important;
}

[data-baseweb="popover"] [role="listbox"],
[data-testid="stSelectboxVirtualDropdown"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  box-shadow: 0 12px 28px var(--shadow) !important;
  color: var(--text) !important;
  width: 340px !important;
  max-width: min(340px,92vw) !important;
  padding: .3rem !important;
  overflow: hidden !important;
}

[role="listbox"] [role="option"] {
  color: var(--text) !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
  word-break: break-word !important;
  line-height: 1.4 !important;
  font-size: .8rem !important;
  padding: .5rem .6rem !important;
  border-radius: 7px !important;
}

[role="listbox"] [role="option"] * {
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

[role="listbox"] [role="option"][aria-selected="true"],
[role="listbox"] [role="option"]:hover {
  background: var(--soft) !important;
}

/* Document filters / table: the type filter buttons and the document list table on the Documents/Dashboard pages. */

[data-testid="stButtonGroup"] {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: .2rem;
  gap: .2rem !important;
}

[data-testid="stButtonGroup"] button {
  border-radius: 7px !important;
  border: none !important;
  background: transparent !important;
  font-size: .76rem !important;
  font-weight: 650 !important;
  color: var(--muted) !important;
  min-height: 1.75rem !important;
  box-shadow: none !important;
}

[data-testid="stButtonGroup"] button[aria-checked="true"] {
  background: var(--soft) !important;
  color: var(--accent) !important;
}

[data-testid="stButtonGroup"] button p {
  font-size: .76rem !important;
  font-weight: 650 !important;
  color: inherit !important;
}

.document-table-head {
  display: grid;
  grid-template-columns: minmax(150px,1fr) 56px 68px 92px 96px;
  gap: .5rem;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding: .7rem .6rem;
  color: var(--subtle);
  font-size: .65rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: .03em;
  margin-top: .4rem;
}

.document-table-head span:nth-child(2),
.document-table-head span:nth-child(3),
.document-row>div:nth-child(2),
.document-row>div:nth-child(3) {
  text-align: center;
}

.document-table-head span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-row {
  display: grid;
  grid-template-columns: minmax(150px,1fr) 56px 68px 92px 96px;
  align-items: center;
  gap: .5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: .62rem .6rem;
  margin: .5rem 0;
  color: var(--text);
  font-size: .74rem;
  transition: border-color .15s ease;
}

.document-row:hover {
  border-color: var(--border-strong);
}

.document-row.selected {
  border-color: var(--accent);
  background: var(--soft);
}

.document-row>div {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-title {
  display: flex;
  align-items: flex-start;
  gap: .5rem;
  min-width: 0;
  overflow: visible !important;
  white-space: normal !important;
}

.doc-title strong {
  display: block;
  max-width: 100%%;
  overflow-wrap: anywhere;
  word-break: break-word;
  white-space: normal;
  font-size: .76rem;
  font-weight: 650;
  line-height: 1.35;
}

.doc-title small {
  display: flex;
  align-items: center;
  gap: .3rem;
  flex-wrap: wrap;
  color: var(--subtle);
  font-size: .65rem;
  margin-top: .25rem;
  overflow: visible;
  white-space: normal;
}

.doc-tag {
  display: inline-block;
  color: var(--muted);
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 0 .38rem;
  font-size: .6rem;
  font-weight: 700;
  letter-spacing: .02em;
}

.doc-file {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  min-width: 34px;
  border-radius: 9px;
  background: var(--surface2);
  color: var(--muted);
}

.doc-file.pdf {
  background: var(--danger-soft);
  color: var(--danger);
}

.doc-file.docx {
  background: var(--soft);
  color: var(--accent);
}

.doc-file.txt {
  background: var(--success-soft);
  color: var(--success);
}

.doc-status {
  display: flex;
  align-items: center;
  gap: .35rem;
  color: var(--success);
  font-weight: 700;
}

.document-count {
  color: var(--muted);
  font-size: .75rem;
  margin-top: .95rem;
}

.doc-row-flat {
  display: flex;
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: .7rem .85rem;
  margin: .5rem 0;
  transition: border-color .15s ease;
}

.doc-row-flat:hover {
  border-color: var(--border-strong);
}

.doc-row-flat .doc-title {
  width: 100%%;
}

.doc-row-flat .doc-title small {
  flex-wrap: wrap;
  row-gap: .2rem;
}

/* Secure assistant / chat: chat bubbles, source chips, and the chat input box used in the assistant panel. */

.assistant-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.security-pill {
  display: inline-flex;
  align-items: center;
  gap: .32rem;
  color: var(--success);
  background: var(--success-soft);
  border: 1px solid rgba(34,197,94,.28);
  border-radius: 7px;
  padding: .36rem .55rem;
  font-size: .71rem;
  font-weight: 700;
  margin-left: .35rem;
}

[data-testid="stChatMessage"] {
  border-radius: 11px !important;
  padding: .75rem .9rem !important;
  margin: 0 0 .7rem !important;
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  gap: .65rem !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
  color: var(--text) !important;
  font-size: .83rem;
  line-height: 1.55;
}

[data-testid="stChatMessage"] p:last-child {
  margin-bottom: 0;
}

[data-testid="stChatMessage"]:has([data-testid*="Avatar"][data-testid*="ser"]) [data-testid*="Avatar"],
[data-testid="stChatMessage"] [data-testid*="AvatarUser"] {
  background: var(--surface) !important;
  color: var(--muted) !important;
  box-shadow: inset 0 0 0 1px var(--border-strong);
}

[data-testid="stChatMessage"]:has([data-testid*="Assistant"]) {
  border-color: rgba(59,107,245,.25) !important;
}

[data-testid="stChatMessage"] [data-testid*="AvatarAssistant"] {
  background: linear-gradient(150deg,var(--accent),var(--accent-strong)) !important;
  color: #fff !important;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: .4rem;
  color: var(--subtle);
  font-size: .68rem;
  font-weight: 700;
  margin-bottom: .35rem;
}

.message-meta.assistant {
  color: var(--accent);
}

.message-meta .icon {
  color: inherit;
}

.source-card {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  background: var(--input);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: .32rem .55rem;
  color: var(--muted) !important;
  font-size: .68rem;
  margin-top: .5rem;
  margin-right: .4rem;
}

.source-card .icon {
  color: var(--subtle);
}

[class*="st-key-ans_hist_"] code {
  color: var(--success) !important;
  background: none !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 .3em !important;
  font-weight: 500 !important;
  font-size: inherit !important;
  font-family: inherit !important;
}

[data-testid="stChatInput"] {
  border: 1px solid var(--border-strong) !important;
  border-radius: 10px !important;
  background: var(--input) !important;
}

[data-testid="stChatInput"] textarea {
  color: var(--text) !important;
}

[data-testid="stChatInput"]>div {
  border-color: var(--border-strong) !important;
  box-shadow: none !important;
}

[data-testid="stChatInput"]:focus-within>div {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--soft) !important;
}

[data-testid="stChatInputSubmitButton"] {
  background: var(--accent) !important;
  border: none !important;
  border-radius: 8px !important;
  transition: background .15s ease !important;
}

[data-testid="stChatInputSubmitButton"]:hover:not(:disabled) {
  background: var(--accent-strong) !important;
}

[data-testid="stChatInputSubmitButton"]:disabled {
  background: var(--surface2) !important;
  opacity: .55 !important;
}

[data-testid="stChatInputSubmitButton"] svg {
  display: none !important;
}

[data-testid="stChatInputSubmitButton"] {
  position: relative !important;
}

[data-testid="stChatInputSubmitButton"]::before {
  content: "";
  position: absolute;
  top: 50%%;
  left: 50%%;
  width: 17px;
  height: 17px;
  transform: translate(-50%%,-50%%);
  background: #fff;
  -webkit-mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="black"><path d="M16.1 260.2c-22.6 12.9-20.5 47.3 3.6 57.3L160 376l0 103.3c0 18.1 14.6 32.7 32.7 32.7c9.7 0 18.9-4.3 25.1-11.8l62-74.3 123.9 51.6c18.9 7.9 40.8-4.5 43.9-24.7l64-416c1.9-12.1-3.4-24.3-13.5-31.2s-23.3-7.5-34-1.4l-448 256zm52.1 25.5L409.7 90.6 190.1 336l1.2 1L68.2 285.7zM403.3 425.4L236.7 355.9 450.8 116.6 403.3 425.4z"/></svg>') center/contain no-repeat;
  mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="black"><path d="M16.1 260.2c-22.6 12.9-20.5 47.3 3.6 57.3L160 376l0 103.3c0 18.1 14.6 32.7 32.7 32.7c9.7 0 18.9-4.3 25.1-11.8l62-74.3 123.9 51.6c18.9 7.9 40.8-4.5 43.9-24.7l64-416c1.9-12.1-3.4-24.3-13.5-31.2s-23.3-7.5-34-1.4l-448 256zm52.1 25.5L409.7 90.6 190.1 336l1.2 1L68.2 285.7zM403.3 425.4L236.7 355.9 450.8 116.6 403.3 425.4z"/></svg>') center/contain no-repeat;
}

[data-testid="stChatInputSubmitButton"]:disabled::before {
  background: var(--subtle);
}

.chat-hint {
  color: var(--subtle);
  font-size: .68rem;
  margin-top: .45rem;
  text-align: right;
}

/* Misc cards: chat history cards and the page footer shown at the bottom of most pages. */

.history-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 11px;
  padding: .9rem 1rem;
}

.history-question {
  color: var(--text);
  font-size: .86rem;
  font-weight: 650;
  margin: .3rem 0;
}

.history-answer {
  color: var(--muted);
  font-size: .8rem;
  line-height: 1.55;
}

.history-answer .pii-highlight {
  color: var(--success);
  font-weight: 500;
  margin: 0 .3em;
}

.history-time {
  color: var(--subtle);
  font-size: .68rem;
  margin-top: .5rem;
}

.app-footer {
  color: var(--subtle);
  font-size: .71rem;
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--border);
  margin-top: 1.3rem;
  padding-top: .85rem;
}

/* Small screens: tighter padding and a simplified document table with fewer columns. */

@media (max-width: 900px) {
  .block-container {
    padding: 4.4rem 1rem 2rem !important;
  }

  .document-table-head,
  .document-row {
    grid-template-columns: minmax(80px,1fr) 46px 60px;
  }

  .document-table-head span:nth-child(4),
  .document-table-head span:nth-child(5),
  .document-row>div:nth-child(4),
  .document-row>div:nth-child(5) {
    display: none;
  }

  .app-footer {
    display: block;
  }
}
</style>"""
        % p,
        unsafe_allow_html=True,
    )
