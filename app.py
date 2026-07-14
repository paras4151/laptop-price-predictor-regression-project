# -*- coding: utf-8 -*-
import streamlit as st
import pickle
import numpy as np
import pandas as pd

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Laptop Price Predictor",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Load Model & Data ───────────────────────────────────────────────────────────
pipe = pickle.load(open('pipe.pkl', 'rb'))
df   = pickle.load(open('df.pkl', 'rb'))

# ════════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — injected once, all custom styling lives here
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600;700&display=swap');

/* ── Color Tokens ─────────────────────────────────────────────────────────── */
:root {
  --bg:      #0a0b0f;
  --card:    rgba(24,26,32,0.85);
  --border:  #2d2f38;
  --accent:  #38E1C6;
  --violet:  #A78BFA;
  --success: #52B788;
  --gold:    #FFB703;
  --text:    #F2F3F5;
  --muted:   #92949c;
}

/* ── Base — make the whole app dark ──────────────────────────────────────── */
html, body,
.stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── Ambient fixed background (behind everything) ─────────────────────────
   z-index: 0 so it sits below Streamlit content (which is z-index > 0).
   pointer-events: none so it never blocks clicks.                          */
#ambient-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  background:
    radial-gradient(ellipse at 20% 20%, rgba(56,225,198,0.06) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(167,139,250,0.05) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 0%, #0d1117 0%, var(--bg) 70%);
}
/* Dot-grid texture — PCB via-hole pattern */
#ambient-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(56,225,198,0.06) 1px, transparent 1px);
  background-size: 28px 28px;
}
/* Vignette */
#ambient-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.65) 100%);
}

/* ── Ensure Streamlit content renders ABOVE the background ────────────────
   Critical fix: the main content block must have a z-index above our bg.  */
[data-testid="stAppViewContainer"] > .main {
  position: relative;
  z-index: 1;
}
[data-testid="stAppViewContainer"] > .main > .block-container {
  position: relative;
  z-index: 1;
  padding: 0 !important;
  max-width: 100% !important;
  min-height: 100vh;
}

/* ── Hide default Streamlit chrome ────────────────────────────────────────
   visibility:hidden keeps layout intact; display:none on Cloud can
   collapse the entire app wrapper.                                         */
#MainMenu, [data-testid="stToolbar"], [data-testid="stDecoration"] {
  display: none !important;
}
header[data-testid="stHeader"], footer, [data-testid="stStatusWidget"] {
  visibility: hidden !important;
  height: 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* ── Floating icons & particles (ambient, CSS-only animations) ────────────
   These fade/bob in via CSS keyframes — no JS required.                    */
.float-icon {
  position: fixed;
  pointer-events: none;
  z-index: 0;      /* behind content, above bg */
  animation: icon-fadein 1.5s ease forwards;
}
.float-icon svg { display: block; }
.fi-cpu    { top: 16vh; left: 6vw;  animation: icon-fadein 1.5s ease forwards, bob-a 5.2s ease-in-out 1.5s infinite; }
.fi-ram    { top: 22vh; right: 8vw; animation: icon-fadein 2s   ease forwards, bob-b 6.8s ease-in-out 2s   infinite; }
.fi-ssd    { bottom: 28vh; left: 4vw;  animation: icon-fadein 1.8s ease forwards, bob-c 4.5s ease-in-out 1.8s infinite; }
.fi-gpu    { bottom: 20vh; right: 6vw; animation: icon-fadein 2.2s ease forwards, bob-d 7.3s ease-in-out 2.2s infinite; }

/* Ambient particles */
.particle {
  position: fixed;
  border-radius: 50%;
  background: var(--accent);
  pointer-events: none;
  z-index: 0;
  animation: particle-rise var(--dur, 8s) linear var(--delay, 0s) infinite;
}

/* ── Hero section ─────────────────────────────────────────────────────────── */
.hero-wrap {
  min-height: 90vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 80px clamp(16px,5vw,80px) 60px;
  animation: fadein-up 0.9s ease both;
}
.hero-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  letter-spacing: 0.25em;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 16px;
  opacity: 0.85;
}
.hero-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(2.4rem, 7vw, 5.5rem);
  font-weight: 700;
  line-height: 1.08;
  letter-spacing: -0.02em;
  color: var(--text);
  margin: 0 0 20px;
}
.hero-title .acc { color: var(--accent); }
.hero-sub {
  font-size: clamp(0.95rem, 1.8vw, 1.15rem);
  color: var(--muted);
  max-width: 520px;
  line-height: 1.65;
  margin: 0 auto 44px;
}
.scroll-cue {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.15em;
  animation: bounce 2.2s ease-in-out infinite;
}

/* ── Configure section wrapper ────────────────────────────────────────────── */
.configure-wrap {
  padding: 60px clamp(16px,5vw,60px) 0;
  animation: fadein-up 1.1s ease both;
}
.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 0.22em;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 6px;
}
.section-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(1.6rem, 3.5vw, 2.4rem);
  font-weight: 600;
  color: var(--text);
  margin: 0 0 32px;
}

/* ── Glass card wrapping the form ─────────────────────────────────────────── */
.glass-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  padding: 40px clamp(16px,3vw,40px) 32px;
  box-shadow: 0 8px 48px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
  margin-bottom: 40px;
}
.group-header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--accent);
  border-bottom: 1px solid rgba(56,225,198,0.18);
  padding-bottom: 8px;
  margin: 28px 0 18px;
}
.group-header:first-child { margin-top: 0; }

/* ── Streamlit widget restyling ───────────────────────────────────────────
   NOTE: These class names target Streamlit's generated DOM. They may shift
   between Streamlit versions — check DevTools if styles stop applying.     */
/* Labels */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
}
/* Selectbox visible box */
[data-testid="stSelectbox"] > div > div {
  background: rgba(14,15,20,0.95) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(56,225,198,0.15) !important;
}
/* Number input */
[data-testid="stNumberInput"] input {
  background: rgba(14,15,20,0.95) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stNumberInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(56,225,198,0.15) !important;
  outline: none !important;
}
/* Dropdown popup */
[data-baseweb="popover"] ul, [role="listbox"] {
  background: #13141a !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}
[role="option"]:hover, [role="option"]:focus {
  background: rgba(56,225,198,0.08) !important;
}

/* ── Predict button ───────────────────────────────────────────────────────── */
[data-testid="stButton"] > button {
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  font-size: 1rem !important;
  letter-spacing: 0.05em !important;
  background: var(--accent) !important;
  color: #0a0b0f !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 14px 48px !important;
  width: 100% !important;
  margin-top: 24px !important;
  cursor: pointer !important;
  box-shadow: 0 0 24px rgba(56,225,198,0.3), 0 4px 16px rgba(0,0,0,0.4) !important;
  transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease !important;
}
[data-testid="stButton"] > button:hover {
  filter: brightness(1.12) !important;
  box-shadow: 0 0 40px rgba(56,225,198,0.5), 0 6px 24px rgba(0,0,0,0.4) !important;
  transform: translateY(-2px) !important;
}
[data-testid="stButton"] > button:active {
  transform: scale(0.97) translateY(0) !important;
}

/* ── Result card ──────────────────────────────────────────────────────────── */
.result-wrap {
  display: flex;
  justify-content: center;
  padding: 20px clamp(16px,5vw,60px) 60px;
  animation: fadein-up 0.7s ease both;
}
.result-card {
  background: var(--card);
  border: 1px solid rgba(56,225,198,0.2);
  border-radius: 20px;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  padding: 48px clamp(24px,4vw,56px);
  max-width: 540px;
  width: 100%;
  text-align: center;
  box-shadow: 0 8px 60px rgba(56,225,198,0.08), inset 0 1px 0 rgba(255,255,255,0.04);
}
.result-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 12px;
}
.result-price {
  font-family: 'JetBrains Mono', monospace;
  font-size: clamp(2.6rem, 7vw, 4.5rem);
  font-weight: 700;
  color: var(--success);
  line-height: 1;
  text-shadow: 0 0 32px rgba(82,183,136,0.4);
}
.result-currency {
  font-size: 0.42em;
  vertical-align: super;
  color: var(--muted);
  font-weight: 400;
}
.gauge-wrap { margin-top: 28px; }
.gauge-labels {
  display: flex;
  justify-content: space-between;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 7px;
}
.gauge-track {
  height: 5px;
  border-radius: 99px;
  background: rgba(255,255,255,0.07);
  overflow: hidden;
}
.gauge-fill {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, var(--accent), var(--violet), var(--gold));
  width: 0%;
  transition: width 1.2s cubic-bezier(0.22,1,0.36,1);
}
.gauge-tier {
  margin-top: 9px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  color: var(--muted);
  letter-spacing: 0.1em;
}

/* ── Footer ───────────────────────────────────────────────────────────────── */
.footer {
  text-align: center;
  padding: 28px 16px;
  font-size: 0.72rem;
  color: var(--muted);
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.1em;
  border-top: 1px solid var(--border);
}

/* ── Keyframes ────────────────────────────────────────────────────────────── */
@keyframes fadein-up {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes bounce {
  0%,100% { transform: translateY(0); }
  50%      { transform: translateY(8px); }
}
@keyframes bob-a {
  0%,100% { transform: translateY(0px) rotate(-2deg); }
  50%      { transform: translateY(-14px) rotate(2deg); }
}
@keyframes bob-b {
  0%,100% { transform: translateY(0px) rotate(1deg); }
  50%      { transform: translateY(-18px) rotate(-1deg); }
}
@keyframes bob-c {
  0%,100% { transform: translateY(0px); }
  50%      { transform: translateY(-12px); }
}
@keyframes bob-d {
  0%,100% { transform: translateY(0px) rotate(2deg); }
  50%      { transform: translateY(-16px) rotate(-2deg); }
}
@keyframes particle-rise {
  0%   { opacity: 0;   transform: translateY(0)    scale(1); }
  10%  { opacity: 0.5; }
  90%  { opacity: 0.15; }
  100% { opacity: 0;   transform: translateY(-80vh) scale(0.5); }
}
@keyframes icon-fadein {
  from { opacity: 0; } to { opacity: 0.15; }
}
@keyframes pulse-travel {
  0%   { left: -10px; opacity: 0; }
  5%   { opacity: 0.9; }
  95%  { opacity: 0.6; }
  100% { left: 101vw; opacity: 0; }
}

/* ── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .float-icon { display: none; }
  .glass-card { padding: 20px 14px; }
  .result-card { padding: 32px 18px; }
}

/* ── Reduced motion ───────────────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    transition-duration: 0.001ms !important;
  }
  .float-icon, .particle { display: none !important; }
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# AMBIENT BACKGROUND + FLOATING ICONS
# Pure HTML — no JS required for visibility. Animations are CSS-only.
# The JS only adds cosmetic pulse dots; if it's blocked, page still works.
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="ambient-bg"></div>

<!-- Floating hardware icons — opacity controlled purely by CSS @keyframes -->
<div class="float-icon fi-cpu" style="top:16vh;left:6vw;">
  <svg width="56" height="56" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="16" y="16" width="32" height="32" rx="3" stroke="#38E1C6" stroke-width="1.5"/>
    <rect x="22" y="22" width="20" height="20" rx="1" stroke="#38E1C6" stroke-width="1.5"/>
    <line x1="24" y1="16" x2="24" y2="10" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="32" y1="16" x2="32" y2="10" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="40" y1="16" x2="40" y2="10" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="24" y1="48" x2="24" y2="54" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="32" y1="48" x2="32" y2="54" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="40" y1="48" x2="40" y2="54" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="16" y1="24" x2="10" y2="24" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="16" y1="32" x2="10" y2="32" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="16" y1="40" x2="10" y2="40" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="48" y1="24" x2="54" y2="24" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="48" y1="32" x2="54" y2="32" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="48" y1="40" x2="54" y2="40" stroke="#38E1C6" stroke-width="1.5" stroke-linecap="round"/>
  </svg>
</div>

<div class="float-icon fi-ram" style="top:22vh;right:8vw;">
  <svg width="70" height="38" viewBox="0 0 72 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="10" width="68" height="22" rx="3" stroke="#A78BFA" stroke-width="1.5"/>
    <rect x="8"  y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
    <rect x="16" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
    <rect x="24" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
    <rect x="32" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
    <rect x="40" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
    <rect x="48" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
    <rect x="56" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
    <line x1="10" y1="4" x2="10" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="18" y1="4" x2="18" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="26" y1="4" x2="26" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="34" y1="4" x2="34" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="42" y1="4" x2="42" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="50" y1="4" x2="50" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="58" y1="4" x2="58" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
  </svg>
</div>

<div class="float-icon fi-ssd" style="bottom:28vh;left:4vw;">
  <svg width="68" height="54" viewBox="0 0 72 56" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="2" width="68" height="52" rx="5" stroke="#38E1C6" stroke-width="1.5"/>
    <rect x="10" y="10" width="30" height="20" rx="2" stroke="#38E1C6" stroke-width="1.5"/>
    <rect x="48" y="10" width="12" height="6" rx="1" fill="rgba(56,225,198,0.15)"/>
    <rect x="48" y="20" width="12" height="6" rx="1" fill="rgba(56,225,198,0.15)"/>
    <rect x="48" y="30" width="12" height="6" rx="1" fill="rgba(56,225,198,0.15)"/>
    <line x1="10" y1="38" x2="62" y2="38" stroke="#38E1C6" stroke-width="1.5" opacity="0.35"/>
    <line x1="10" y1="44" x2="40" y2="44" stroke="#38E1C6" stroke-width="1.5" opacity="0.25"/>
  </svg>
</div>

<div class="float-icon fi-gpu" style="bottom:20vh;right:6vw;">
  <svg width="78" height="54" viewBox="0 0 80 56" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="8" width="76" height="40" rx="5" stroke="#FFB703" stroke-width="1.5"/>
    <rect x="10" y="16" width="28" height="24" rx="3" stroke="#FFB703" stroke-width="1.5"/>
    <circle cx="24" cy="28" r="7" stroke="#FFB703" stroke-width="1.5"/>
    <rect x="44" y="16" width="8" height="8" rx="1" fill="rgba(255,183,3,0.15)"/>
    <rect x="56" y="16" width="8" height="8" rx="1" fill="rgba(255,183,3,0.15)"/>
    <rect x="44" y="28" width="8" height="8" rx="1" fill="rgba(255,183,3,0.15)"/>
    <rect x="56" y="28" width="8" height="8" rx="1" fill="rgba(255,183,3,0.15)"/>
    <line x1="16" y1="48" x2="16" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
    <line x1="24" y1="48" x2="24" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
    <line x1="32" y1="48" x2="32" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
    <line x1="40" y1="48" x2="40" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
    <line x1="48" y1="48" x2="48" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
    <line x1="56" y1="48" x2="56" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
  </svg>
</div>

<!-- Ambient particles (CSS-animated, no JS) -->
<div class="particle" style="width:3px;height:3px;left:10vw;bottom:0;--dur:9s;--delay:-2s;"></div>
<div class="particle" style="width:2px;height:2px;left:22vw;bottom:0;--dur:7s;--delay:-5s;"></div>
<div class="particle" style="width:4px;height:4px;left:35vw;bottom:0;--dur:11s;--delay:-1s;"></div>
<div class="particle" style="width:2px;height:2px;left:48vw;bottom:0;--dur:8s;--delay:-7s;"></div>
<div class="particle" style="width:3px;height:3px;left:60vw;bottom:0;--dur:10s;--delay:-3s;"></div>
<div class="particle" style="width:2px;height:2px;left:72vw;bottom:0;--dur:6s;--delay:-9s;"></div>
<div class="particle" style="width:3px;height:3px;left:85vw;bottom:0;--dur:12s;--delay:-4s;"></div>
<div class="particle" style="width:2px;height:2px;left:15vw;bottom:0;--dur:8s;--delay:-6s;"></div>
<div class="particle" style="width:4px;height:4px;left:55vw;bottom:0;--dur:9s;--delay:-0.5s;"></div>
<div class="particle" style="width:2px;height:2px;left:78vw;bottom:0;--dur:7s;--delay:-8s;"></div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# HERO SECTION
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
  <p class="hero-tag">// AI-Powered · Spec Analysis · ML Model</p>
  <h1 class="hero-title">LAPTOP PRICE<br><span class="acc">PREDICTOR</span></h1>
  <p class="hero-sub">
    Configure your ideal laptop specifications below and our
    machine-learning pipeline will estimate the market price instantly.
  </p>
  <div class="scroll-cue">
    <span>SCROLL TO CONFIGURE</span>
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38E1C6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="6 9 12 15 18 9"/>
    </svg>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURE SECTION — section header (pure HTML)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="configure-wrap">
  <p class="section-label">// Spec Configuration</p>
  <h2 class="section-title">Build Your Machine</h2>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# FORM — all inputs inside a glass card (CSS-styled)
# The card background is applied via a wrapping div injected before/after
# Streamlit widget calls. Each st.markdown injects a separate DOM node, so
# the card background is applied with CSS rather than actual HTML nesting.
# ════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

# ── Identity ─────────────────────────────────────────────────────────────────
st.markdown('<p class="group-header">⬡ &nbsp;Identity</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    company = st.selectbox('Brand', df['Company'].unique())
with col2:
    type = st.selectbox('Type', df['TypeName'].unique())

# ── Display ──────────────────────────────────────────────────────────────────
st.markdown('<p class="group-header">⬡ &nbsp;Display</p>', unsafe_allow_html=True)
col3, col4, col5, col6 = st.columns(4)
with col3:
    touchscreen = st.selectbox('Touchscreen', ['No', 'Yes'])
with col4:
    ips = st.selectbox('IPS Panel', ['No', 'Yes'])
with col5:
    screen_size = st.number_input('Screen Size (in)', min_value=1.0, value=13.0)
with col6:
    resolution = st.selectbox('Resolution',
        ['1920x1080','1366x768','1600x900','3840x2160',
         '3200x1800','2880x1800','2560x1600','2560x1440','2304x1440'])

# ── Performance ──────────────────────────────────────────────────────────────
st.markdown('<p class="group-header">⬡ &nbsp;Performance</p>', unsafe_allow_html=True)
col7, col8, col9 = st.columns(3)
with col7:
    cpu = st.selectbox('CPU Brand', df['Cpu brand'].unique())
with col8:
    ram = st.selectbox('RAM (GB)', [2, 4, 6, 8, 12, 16, 24, 32, 64])
with col9:
    gpu = st.selectbox('GPU Brand', df['Gpu brand'].unique())

# ── Storage ───────────────────────────────────────────────────────────────────
st.markdown('<p class="group-header">⬡ &nbsp;Storage</p>', unsafe_allow_html=True)
col10, col11 = st.columns(2)
with col10:
    hdd = st.selectbox('HDD (GB)', [0, 128, 256, 512, 1024, 2048])
with col11:
    ssd = st.selectbox('SSD (GB)', [0, 8, 128, 256, 512, 1024])

# ── System ────────────────────────────────────────────────────────────────────
st.markdown('<p class="group-header">⬡ &nbsp;System</p>', unsafe_allow_html=True)
col12, col13 = st.columns(2)
with col12:
    weight = st.number_input('Weight (kg)', min_value=0.1, value=1.5)
with col13:
    os = st.selectbox('OS', df['os'].unique())

st.markdown('</div>', unsafe_allow_html=True)   # close glass-card


# ════════════════════════════════════════════════════════════════════════════════
# PREDICT BUTTON
# ════════════════════════════════════════════════════════════════════════════════
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    predict_clicked = st.button('⚡  Predict Price')


# ════════════════════════════════════════════════════════════════════════════════
# RESULT — original prediction logic unchanged
# ════════════════════════════════════════════════════════════════════════════════
if predict_clicked:
    touchscreen_val = 1 if touchscreen == 'Yes' else 0
    ips_val         = 1 if ips == 'Yes' else 0

    X_res = int(resolution.split('x')[0])
    Y_res = int(resolution.split('x')[1])
    ppi   = ((X_res ** 2) + (Y_res ** 2)) ** 0.5 / screen_size

    # Build a single-row DataFrame with exact column names the pipeline expects
    query = pd.DataFrame([{
        'Company':    company,
        'TypeName':   type,
        'Ram':        int(ram),
        'Weight':     float(weight),
        'Touchscreen':touchscreen_val,
        'Ips':        ips_val,
        'ppi':        ppi,
        'Cpu brand':  cpu,
        'HDD':        int(hdd),
        'SSD':        int(ssd),
        'Gpu brand':  gpu,
        'os':         os,
    }])

    predicted_price = int(np.exp(pipe.predict(query)[0]))

    # Price tier for gauge
    if predicted_price < 40000:
        tier_label = "BUDGET TIER"
        gauge_pct  = min(int((predicted_price / 40000) * 33), 33)
    elif predicted_price < 90000:
        tier_label = "MID-RANGE TIER"
        gauge_pct  = 33 + min(int(((predicted_price - 40000) / 50000) * 34), 34)
    else:
        tier_label = "PREMIUM TIER"
        gauge_pct  = 67 + min(int(((predicted_price - 90000) / 110000) * 33), 33)
    gauge_pct = min(gauge_pct, 100)

    # ── Result card with JS count-up animation ─────────────────────────────
    # The count-up JS is isolated and purely cosmetic; the price is also
    # displayed as plain text so it's readable even if JS is blocked.
    st.markdown(f"""
<div class="result-wrap">
  <div class="result-card">
    <p class="result-label">// Estimated Market Price</p>
    <div class="result-price">
      <span class="result-currency">&#8377;</span><span id="price-display">{predicted_price:,}</span>
    </div>
    <div class="gauge-wrap">
      <div class="gauge-labels">
        <span>Budget</span><span>Mid-Range</span><span>Premium</span>
      </div>
      <div class="gauge-track">
        <div class="gauge-fill" id="gfill" style="width:{gauge_pct}%"></div>
      </div>
      <p class="gauge-tier">{tier_label}</p>
    </div>
  </div>
</div>

<script>
/* COUNT-UP ANIMATION
   Cosmetic only — price is already rendered as plain text above.
   Counts from 0 to target over ~850ms using easeOutQuart easing. */
(function() {{
  var target = {predicted_price};
  var el = document.getElementById('price-display');
  if (!el) return;
  var start = performance.now();
  var dur = 850;
  function ease(t) {{ return 1 - Math.pow(1 - t, 4); }}
  function step(now) {{
    var p = Math.min((now - start) / dur, 1);
    el.textContent = Math.round(ease(p) * target).toLocaleString('en-IN');
    if (p < 1) requestAnimationFrame(step);
    else el.textContent = target.toLocaleString('en-IN');
  }}
  requestAnimationFrame(step);
}})();
</script>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  LAPTOP PRICE PREDICTOR &nbsp;·&nbsp; STREAMLIT &nbsp;·&nbsp; RANDOM FOREST PIPELINE
</div>
""", unsafe_allow_html=True)
