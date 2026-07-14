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
# GLOBAL CSS INJECTION
# All custom styling lives here in one well-commented block.
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600;700&display=swap');

/* ── Color Tokens ─────────────────────────────────────────────────────────── */
:root {
  --bg:        #0a0b0f;
  --card:      rgba(24,26,32,0.82);
  --border:    #2d2f38;
  --accent:    #38E1C6;
  --violet:    #A78BFA;
  --success:   #52B788;
  --gold:      #FFB703;
  --text:      #F2F3F5;
  --muted:     #92949c;
}

/* ── Global Reset ─────────────────────────────────────────────────────────── */
html, body {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif;
}
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* Hide Streamlit chrome — use visibility:hidden NOT display:none so the
   layout wrapper stays intact on Streamlit Cloud (display:none can collapse
   the entire app container in some Cloud versions) */
#MainMenu { display: none !important; }
header[data-testid="stHeader"],
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
  visibility: hidden !important;
  height: 0 !important;
  min-height: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
}

/* Block container — keep a minimum height so Streamlit renders content */
[data-testid="stAppViewContainer"] > .main > .block-container,
[data-testid="block-container"] {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  max-width: 100% !important;
  min-height: 100vh;
}

/* ── Fixed Ambient Background Layer ──────────────────────────────────────── */
/* This sits behind everything (z-index: -1). Populated by JS. */
#ambient-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
  background: radial-gradient(ellipse at 50% 0%, #0d1117 0%, var(--bg) 70%);
}

/* Dot-grid texture — PCB via-holes feel */
#ambient-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(56,225,198,0.07) 1px, transparent 1px);
  background-size: 28px 28px;
  pointer-events: none;
}

/* Vignette — darkens edges for cinematic frame */
#ambient-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.7) 100%);
  pointer-events: none;
}

/* Glow orbs — slowly drifting teal/violet blobs for depth */
.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.18;
  pointer-events: none;
}
.glow-orb.teal  { background: var(--accent); animation: orb-drift-1 18s ease-in-out infinite; }
.glow-orb.violet{ background: var(--violet); animation: orb-drift-2 22s ease-in-out infinite; }

/* PCB trace lines — teal hairlines at low opacity for texture */
.trace-h, .trace-v {
  position: absolute;
  background: linear-gradient(90deg, transparent, rgba(56,225,198,0.12), transparent);
  pointer-events: none;
}
.trace-h { height: 1px; width: 100%; }
.trace-v { width: 1px; height: 100%; background: linear-gradient(180deg, transparent, rgba(56,225,198,0.12), transparent); }

/* Data pulse dots — travel along traces */
.pulse-dot {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px 2px var(--accent);
  pointer-events: none;
  opacity: 0;
}

/* Ambient particles — dust drifting upward */
.particle {
  position: absolute;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0;
  pointer-events: none;
  animation: particle-rise var(--dur, 8s) linear var(--delay, 0s) infinite;
}

/* Floating component icons — parallax + bob */
.float-icon {
  position: fixed;
  pointer-events: none;
  z-index: 0;
  transition: transform 0.12s ease-out;
  will-change: transform;
}
.float-icon svg { display: block; opacity: 0.18; }
/* Each icon independently bobs up/down */
.float-icon .icon-inner { animation: bob var(--bob-dur, 5s) ease-in-out infinite; }

/* ── Section Layout ───────────────────────────────────────────────────────── */
.section {
  position: relative;
  z-index: 1;
  padding: 0 clamp(16px, 5vw, 80px);
}

/* Scroll-reveal: sections start hidden, JS adds .visible class */
.reveal {
  opacity: 0;
  transform: translateY(32px);
  transition: opacity 0.7s ease, transform 0.7s ease;
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ── Hero Section ─────────────────────────────────────────────────────────── */
#hero {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding-top: 80px;
}
.hero-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  letter-spacing: 0.25em;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 16px;
  opacity: 0.8;
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
.hero-title .accent { color: var(--accent); }
.hero-sub {
  font-size: clamp(0.95rem, 1.8vw, 1.2rem);
  color: var(--muted);
  max-width: 520px;
  line-height: 1.6;
  margin: 0 auto 48px;
}
/* Animated scroll cue arrow */
.scroll-cue {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  animation: bounce 2s ease-in-out infinite;
}
.scroll-cue svg { stroke: var(--accent); }

/* ── Glass Card (Configure section) ──────────────────────────────────────── */
#configure {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding-top: 80px;
  padding-bottom: 80px;
}
.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  letter-spacing: 0.22em;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 8px;
}
.section-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(1.6rem, 3.5vw, 2.6rem);
  font-weight: 600;
  color: var(--text);
  margin: 0 0 40px;
}
.glass-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 40px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
}
.group-header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--accent);
  border-bottom: 1px solid rgba(56,225,198,0.15);
  padding-bottom: 8px;
  margin-bottom: 20px;
  margin-top: 32px;
}
.group-header:first-child { margin-top: 0; }

/* ── Streamlit Widget Overrides ───────────────────────────────────────────── */
/* NOTE: These class names target Streamlit's generated DOM.
   They may shift between Streamlit versions — check in-browser DevTools if
   styles don't apply after an upgrade. */

/* Label text */
[data-testid="stWidgetLabel"] p,
label, .stSelectbox label, .stNumberInput label,
.stSlider label {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
  margin-bottom: 4px !important;
}

/* Selectbox & Number Input boxes */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] > div > div > input {
  background: rgba(18,20,26,0.9) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.92rem !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stNumberInput"] > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(56,225,198,0.18) !important;
}

/* Dropdown popup background */
[data-testid="stSelectbox"] ul,
[data-baseweb="popover"] ul,
[role="listbox"] {
  background: #16181f !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}
[role="option"]:hover {
  background: rgba(56,225,198,0.08) !important;
}

/* ── Predict Button ───────────────────────────────────────────────────────── */
/* Solid accent with teal glow; scales down slightly on click for tactile feel */
[data-testid="stButton"] > button {
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  font-size: 1rem !important;
  letter-spacing: 0.04em !important;
  background: var(--accent) !important;
  color: #0a0b0f !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 14px 48px !important;
  cursor: pointer !important;
  transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease !important;
  box-shadow: 0 0 20px rgba(56,225,198,0.35), 0 4px 16px rgba(0,0,0,0.4) !important;
  margin-top: 32px !important;
  width: 100% !important;
}
[data-testid="stButton"] > button:hover {
  filter: brightness(1.1) !important;
  box-shadow: 0 0 36px rgba(56,225,198,0.5), 0 6px 24px rgba(0,0,0,0.4) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active {
  transform: scale(0.97) !important;
}

/* ── Result Section ───────────────────────────────────────────────────────── */
#result {
  min-height: 50vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding-top: 60px;
  padding-bottom: 80px;
}
.result-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 48px 56px;
  max-width: 560px;
  width: 100%;
  box-shadow: 0 8px 60px rgba(56,225,198,0.1), inset 0 1px 0 rgba(255,255,255,0.04);
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
  font-size: clamp(2.8rem, 7vw, 4.5rem);
  font-weight: 700;
  color: var(--success);
  line-height: 1;
  text-shadow: 0 0 30px rgba(82,183,136,0.35);
}
.result-currency {
  font-size: 0.45em;
  vertical-align: super;
  color: var(--muted);
  font-weight: 400;
}
/* Value gauge bar */
.gauge-wrap {
  margin-top: 28px;
}
.gauge-labels {
  display: flex;
  justify-content: space-between;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 8px;
}
.gauge-track {
  height: 6px;
  border-radius: 99px;
  background: rgba(255,255,255,0.06);
  overflow: hidden;
  position: relative;
}
.gauge-fill {
  height: 100%;
  border-radius: 99px;
  width: 0%;
  transition: width 1.1s cubic-bezier(0.22,1,0.36,1);
  background: linear-gradient(90deg, var(--accent), var(--violet), var(--gold));
}
.gauge-tier {
  margin-top: 10px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--muted);
  letter-spacing: 0.1em;
}

/* ── Footer ───────────────────────────────────────────────────────────────── */
#footer {
  text-align: center;
  padding: 24px;
  font-size: 0.75rem;
  color: var(--muted);
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.1em;
  border-top: 1px solid var(--border);
}

/* ── Keyframe Animations ──────────────────────────────────────────────────── */

/* Glow orbs drifting */
@keyframes orb-drift-1 {
  0%,100% { transform: translate(0,0); }
  33%      { transform: translate(80px,-60px); }
  66%      { transform: translate(-60px,40px); }
}
@keyframes orb-drift-2 {
  0%,100% { transform: translate(0,0); }
  40%     { transform: translate(-100px,70px); }
  70%     { transform: translate(50px,-80px); }
}

/* Floating icons bobbing */
@keyframes bob {
  0%,100% { transform: translateY(0px); }
  50%     { transform: translateY(-14px); }
}

/* Particles rising upward and fading */
@keyframes particle-rise {
  0%   { opacity: 0; transform: translateY(0) scale(1); }
  10%  { opacity: 0.5; }
  90%  { opacity: 0.2; }
  100% { opacity: 0; transform: translateY(-80vh) scale(0.6); }
}

/* Scroll-cue bounce */
@keyframes bounce {
  0%,100% { transform: translateY(0); }
  50%     { transform: translateY(8px); }
}

/* ── Responsive Overrides ─────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .float-icon { display: none; }     /* hide parallax icons on touch */
  .glass-card { padding: 24px 16px; }
  .result-card { padding: 32px 20px; }
  .hero-title { font-size: 2.2rem; }
}

/* ── Reduced-Motion Fallback ──────────────────────────────────────────────── */
/* Removes all animations for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    transition-duration: 0.001ms !important;
  }
  .float-icon, .particle, .pulse-dot { display: none !important; }
  .reveal { opacity: 1 !important; transform: none !important; }
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# AMBIENT BACKGROUND + PARALLAX JAVASCRIPT
# Injected once at top. Creates all generative background elements.
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="ambient-bg">
  <!-- Glow orbs -->
  <div class="glow-orb teal"   style="width:520px;height:520px;top:-100px;left:-80px;"></div>
  <div class="glow-orb violet" style="width:400px;height:400px;bottom:60px;right:-60px;"></div>

  <!-- Floating component SVG icons — each gets its depth value via data-depth -->
  <!-- CPU Icon -->
  <div class="float-icon" id="fi-cpu" data-depth="0.06" style="top:18vh;left:8vw;">
    <div class="icon-inner" style="--bob-dur:5.2s">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
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
  </div>

  <!-- RAM Stick Icon -->
  <div class="float-icon" id="fi-ram" data-depth="0.04" style="top:25vh;right:10vw;">
    <div class="icon-inner" style="--bob-dur:6.8s">
      <svg width="72" height="40" viewBox="0 0 72 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="10" width="68" height="22" rx="3" stroke="#A78BFA" stroke-width="1.5"/>
        <rect x="8"  y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
        <rect x="16" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
        <rect x="24" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
        <rect x="32" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
        <rect x="40" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
        <rect x="48" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
        <rect x="56" y="10" width="4" height="22" fill="rgba(167,139,250,0.12)"/>
        <line x1="10" y1="4"  x2="10" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="18" y1="4"  x2="18" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="26" y1="4"  x2="26" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="34" y1="4"  x2="34" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="42" y1="4"  x2="42" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="50" y1="4"  x2="50" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="58" y1="4"  x2="58" y2="10" stroke="#A78BFA" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </div>
  </div>

  <!-- SSD Icon -->
  <div class="float-icon" id="fi-ssd" data-depth="0.08" style="bottom:30vh;left:5vw;">
    <div class="icon-inner" style="--bob-dur:4.5s">
      <svg width="72" height="56" viewBox="0 0 72 56" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="68" height="52" rx="5" stroke="#38E1C6" stroke-width="1.5"/>
        <rect x="10" y="10" width="30" height="20" rx="2" stroke="#38E1C6" stroke-width="1.5"/>
        <rect x="48" y="10" width="12" height="6"  rx="1" fill="rgba(56,225,198,0.15)"/>
        <rect x="48" y="20" width="12" height="6"  rx="1" fill="rgba(56,225,198,0.15)"/>
        <rect x="48" y="30" width="12" height="6"  rx="1" fill="rgba(56,225,198,0.15)"/>
        <line x1="10" y1="38" x2="62" y2="38" stroke="#38E1C6" stroke-width="1.5" opacity="0.4"/>
        <line x1="10" y1="44" x2="40" y2="44" stroke="#38E1C6" stroke-width="1.5" opacity="0.3"/>
      </svg>
    </div>
  </div>

  <!-- GPU Icon -->
  <div class="float-icon" id="fi-gpu" data-depth="0.05" style="bottom:22vh;right:7vw;">
    <div class="icon-inner" style="--bob-dur:7.3s">
      <svg width="80" height="56" viewBox="0 0 80 56" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="8" width="76" height="40" rx="5" stroke="#FFB703" stroke-width="1.5"/>
        <rect x="10" y="16" width="28" height="24" rx="3" stroke="#FFB703" stroke-width="1.5"/>
        <circle cx="24" cy="28" r="7" stroke="#FFB703" stroke-width="1.5"/>
        <rect x="44" y="16" width="8"  height="8"  rx="1" fill="rgba(255,183,3,0.15)"/>
        <rect x="56" y="16" width="8"  height="8"  rx="1" fill="rgba(255,183,3,0.15)"/>
        <rect x="44" y="28" width="8"  height="8"  rx="1" fill="rgba(255,183,3,0.15)"/>
        <rect x="56" y="28" width="8"  height="8"  rx="1" fill="rgba(255,183,3,0.15)"/>
        <line x1="16" y1="48" x2="16" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
        <line x1="24" y1="48" x2="24" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
        <line x1="32" y1="48" x2="32" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
        <line x1="40" y1="48" x2="40" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
        <line x1="48" y1="48" x2="48" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
        <line x1="56" y1="48" x2="56" y2="54" stroke="#FFB703" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </div>
  </div>
</div>

<script>
/*
 * AMBIENT BACKGROUND GENERATOR
 * Programmatically creates PCB traces, data pulses, and ambient particles.
 * All elements are appended to #ambient-bg so they sit behind all content.
 * Respects prefers-reduced-motion by skipping animation setup.
 */
(function() {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const bg = document.getElementById('ambient-bg');
  if (!bg) return;

  // ── 1. PCB horizontal & vertical traces ─────────────────────────────────
  // Creates a grid of faint teal lines at randomized positions.
  function createTraces() {
    const positions = [15, 28, 45, 60, 75, 88]; // % of viewport
    positions.forEach(pct => {
      const h = document.createElement('div');
      h.className = 'trace-h';
      h.style.top = pct + 'vh';
      bg.appendChild(h);

      const v = document.createElement('div');
      v.className = 'trace-v';
      v.style.left = pct + 'vw';
      bg.appendChild(v);
    });
  }

  // ── 2. Data pulse dots ────────────────────────────────────────────────────
  // Creates small glowing dots that travel along the trace lines.
  function createPulses() {
    if (prefersReduced) return;
    const traceYs = [15, 28, 45, 60, 75]; // match trace positions in vh
    traceYs.forEach((yPct, i) => {
      const dot = document.createElement('div');
      dot.className = 'pulse-dot';
      dot.style.top = 'calc(' + yPct + 'vh - 2.5px)';
      dot.style.left = '0';
      bg.appendChild(dot);

      // Animate the dot travelling across the screen
      const duration = 4000 + i * 1100;
      const delay = i * 700;
      function animatePulse() {
        dot.style.opacity = '0';
        dot.style.transition = 'none';
        dot.style.left = '-10px';
        setTimeout(() => {
          dot.style.transition = 'left ' + duration + 'ms linear, opacity 300ms ease';
          dot.style.left = '101vw';
          dot.style.opacity = '0.9';
          setTimeout(() => { dot.style.opacity = '0'; }, duration - 300);
          setTimeout(animatePulse, duration + 600);
        }, 50);
      }
      setTimeout(animatePulse, delay);
    });
  }

  // ── 3. Ambient particles ──────────────────────────────────────────────────
  // Creates ~14 small glowing dots that drift upward like server-room dust.
  function createParticles() {
    if (prefersReduced) return;
    const count = 14;
    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      const size = 2 + Math.random() * 3;
      p.style.cssText = [
        'width:' + size + 'px',
        'height:' + size + 'px',
        'left:' + (Math.random() * 100) + 'vw',
        'bottom:0',
        '--dur:' + (7 + Math.random() * 8) + 's',
        '--delay:-' + (Math.random() * 10) + 's',
        'opacity:0',
      ].join(';');
      bg.appendChild(p);
    }
  }

  // ── 4. Parallax: cursor-reactive floating icons ───────────────────────────
  // Each icon has a data-depth attribute. On mousemove, shift each icon
  // OPPOSITE to cursor offset scaled by depth, so deeper icons move less.
  function initParallax() {
    if (prefersReduced) return;
    const isTouchDevice = window.matchMedia('(max-width:640px)').matches;
    if (isTouchDevice) return;

    const icons = document.querySelectorAll('.float-icon');
    window.addEventListener('mousemove', function(e) {
      const cx = window.innerWidth / 2;
      const cy = window.innerHeight / 2;
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;
      icons.forEach(icon => {
        const depth = parseFloat(icon.dataset.depth || 0.05);
        // Shift opposite to cursor (parallax effect), scale by depth
        const ox = -dx * depth * 1.4;
        const oy = -dy * depth * 1.4;
        // Apply only the parallax offset here; CSS handles the bob animation
        // on .icon-inner so the two transforms don't conflict.
        icon.style.transform = 'translate(' + ox + 'px, ' + oy + 'px)';
      });
    });
  }

  // ── 5. Scroll background parallax ────────────────────────────────────────
  // Shifts the circuit background layer slightly with scroll for depth.
  function initScrollParallax() {
    if (prefersReduced) return;
    window.addEventListener('scroll', function() {
      bg.style.transform = 'translateY(' + (window.scrollY * 0.08) + 'px)';
    }, { passive: true });
  }

  // ── 6. Scroll reveal (IntersectionObserver) ───────────────────────────────
  // Adds .visible to .reveal sections as they scroll into view.
  function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
        }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }

  // Run everything
  createTraces();
  createPulses();
  createParticles();
  initParallax();
  initScrollParallax();
  // Delay reveal init so Streamlit has time to render the sections
  setTimeout(initScrollReveal, 400);
})();
</script>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — HERO
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="hero" class="section reveal">
  <p class="hero-tag">// AI-Powered Spec Analysis</p>
  <h1 class="hero-title">LAPTOP PRICE<br><span class="accent">PREDICTOR</span></h1>
  <p class="hero-sub">Configure your ideal laptop specifications below and our machine-learning model will reveal the estimated market price in real time.</p>
  <div class="scroll-cue">
    <span>CONFIGURE</span>
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="6 9 12 15 18 9"/>
    </svg>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CONFIGURE (Form)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="configure" class="section reveal">
  <p class="section-label">// Spec Configuration</p>
  <h2 class="section-title">Build Your Machine</h2>
  <div class="glass-card">
    <p class="group-header">⬡ Identity</p>
""", unsafe_allow_html=True)

# ── Identity Group: Brand & Type ─────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    company = st.selectbox('Brand', df['Company'].unique())
with col2:
    type = st.selectbox('Type', df['TypeName'].unique())

st.markdown('<p class="group-header">⬡ Display</p>', unsafe_allow_html=True)

# ── Display Group ────────────────────────────────────────────────────────────
col3, col4, col5, col6 = st.columns(4)
with col3:
    touchscreen = st.selectbox('Touchscreen', ['No', 'Yes'])
with col4:
    ips = st.selectbox('IPS', ['No', 'Yes'])
with col5:
    screen_size = st.number_input('Screen Size (in)', min_value=1.0, value=13.0)
with col6:
    resolution = st.selectbox('Resolution',
        ['1920x1080', '1366x768', '1600x900', '3840x2160',
         '3200x1800', '2880x1800', '2560x1600', '2560x1440', '2304x1440'])

st.markdown('<p class="group-header">⬡ Performance</p>', unsafe_allow_html=True)

# ── Performance Group: CPU, RAM, GPU ─────────────────────────────────────────
col7, col8, col9 = st.columns(3)
with col7:
    cpu = st.selectbox('CPU Brand', df['Cpu brand'].unique())
with col8:
    ram = st.selectbox('RAM (GB)', [2, 4, 6, 8, 12, 16, 24, 32, 64])
with col9:
    gpu = st.selectbox('GPU Brand', df['Gpu brand'].unique())

st.markdown('<p class="group-header">⬡ Storage</p>', unsafe_allow_html=True)

# ── Storage Group: HDD, SSD ──────────────────────────────────────────────────
col10, col11 = st.columns(2)
with col10:
    hdd = st.selectbox('HDD (GB)', [0, 128, 256, 512, 1024, 2048])
with col11:
    ssd = st.selectbox('SSD (GB)', [0, 8, 128, 256, 512, 1024])

st.markdown('<p class="group-header">⬡ System</p>', unsafe_allow_html=True)

# ── System Group: Weight, OS ─────────────────────────────────────────────────
col12, col13 = st.columns(2)
with col12:
    weight = st.number_input('Weight (kg)', min_value=0.1, value=1.5)
with col13:
    os = st.selectbox('OS', df['os'].unique())

# Close glass-card and configure section divs
st.markdown("</div></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PREDICT BUTTON
# ════════════════════════════════════════════════════════════════════════════════
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    predict_clicked = st.button('⚡  Predict Price')


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — RESULT
# Uses the exact original query-building and pipe.predict() logic.
# ════════════════════════════════════════════════════════════════════════════════
if predict_clicked:
    # ── Original prediction logic (unchanged) ────────────────────────────────
    touchscreen_val = 1 if touchscreen == 'Yes' else 0
    ips_val = 1 if ips == 'Yes' else 0

    X_res = int(resolution.split('x')[0])
    Y_res = int(resolution.split('x')[1])
    ppi = ((X_res ** 2) + (Y_res ** 2)) ** 0.5 / screen_size

    # Build a single-row DataFrame with the exact column names/dtypes the
    # pipeline was trained on. Passing a plain numpy array here silently
    # casts every value (including the numeric ones) to strings, which is
    # what caused prediction to fail before.
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

    # ── Determine price tier for gauge ───────────────────────────────────────
    # Budget < 40k, Mid 40k–90k, Premium > 90k (INR ballpark for the dataset)
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

    # ── Animated result reveal ────────────────────────────────────────────────
    # Inject HTML + a small JS snippet that:
    #   1. Counts the displayed number up from 0 to predicted_price (~800ms)
    #   2. Animates the gauge bar width after a short delay
    st.markdown(f"""
<div id="result" class="section reveal visible">
  <div class="result-card">
    <p class="result-label">// Estimated Market Price</p>
    <div class="result-price">
      <span class="result-currency">₹</span><span id="price-counter">0</span>
    </div>
    <div class="gauge-wrap">
      <div class="gauge-labels">
        <span>Budget</span><span>Mid-Range</span><span>Premium</span>
      </div>
      <div class="gauge-track">
        <div class="gauge-fill" id="gauge-fill"></div>
      </div>
      <p class="gauge-tier" id="gauge-tier">{tier_label}</p>
    </div>
  </div>
</div>

<script>
/*
 * PRICE COUNT-UP ANIMATION
 * Animates the displayed number from 0 to the final predicted price
 * over ~800ms using requestAnimationFrame for smooth easing.
 */
(function() {{
  const target   = {predicted_price};
  const duration = 820; // ms
  const el       = document.getElementById('price-counter');
  const gaugeFill= document.getElementById('gauge-fill');
  const gaugeTarget = {gauge_pct};

  if (!el) return;

  const start = performance.now();
  function easeOutQuart(t) {{ return 1 - Math.pow(1 - t, 4); }}

  function step(now) {{
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased    = easeOutQuart(progress);
    const current  = Math.round(eased * target);
    el.textContent = current.toLocaleString('en-IN');
    if (progress < 1) {{
      requestAnimationFrame(step);
    }} else {{
      el.textContent = target.toLocaleString('en-IN');
      // Animate gauge fill after price count-up completes
      setTimeout(() => {{
        if (gaugeFill) gaugeFill.style.width = gaugeTarget + '%';
      }}, 100);
    }}
  }}

  requestAnimationFrame(step);
}})();
</script>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="footer">
  LAPTOP PRICE PREDICTOR &nbsp;·&nbsp; BUILT WITH STREAMLIT &nbsp;·&nbsp; ML MODEL: RANDOM FOREST PIPELINE
</div>
""", unsafe_allow_html=True)
