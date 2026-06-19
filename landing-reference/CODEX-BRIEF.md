# cv2job Landing Page → Streamlit Adaptation Brief

> Handoff document for Codex (or any coding agent). Read this top-to-bottom before touching any files.

---

## 1. Goal

The cv2job repo (`https://github.com/RuiRafael11/cv2job`) is a Streamlit + FastAPI SaaS app with a sophisticated dark-theme dashboard UI defined in `ui/css.py` and `ui/dashboard.py`. A separate Next.js 16 landing page was designed to match the project's brand. This brief describes how to adapt the landing page's design system to either:

- **(A) Port the design tokens into the existing Streamlit UI** (`ui/css.py`) so the in-app experience matches the marketing site, OR
- **(B) Serve the landing page as a static HTML page from FastAPI** so the whole product lives under one backend.

Pick (A) if you want consistency. Pick (B) if you want one deployment. Both are valid; do not attempt both in the same pass.

---

## 2. Source files (already in this repo)

```
landing-reference/
├── globals.css                     ← design tokens, animations, utilities
├── layout.tsx                      ← font loading (Playfair + Inter + IBM Plex Mono)
├── page.tsx                        ← page composition (section order)
└── landing-components/
    ├── AnimatedSection.tsx         ← scroll-triggered fade/slide helpers
    ├── AtsGauge.tsx                ← circular SVG gauge + sub-score circles
    ├── AuroraBackground.tsx        ← drifting gradient blobs
    ├── Brand.tsx                   ← wordmark + section badge
    ├── Navbar.tsx                  ← sticky scroll-aware nav
    ├── Hero.tsx                    ← hero with ATS gauge mockup
    ├── TrustBar.tsx                ← stats + marquee
    ├── Problem.tsx                 ← 3 pain-point cards
    ├── Features.tsx                ← 6-feature grid
    ├── HowItWorks.tsx              ← 5-step timeline
    ├── AtsDemo.tsx                 ← interactive Before/After toggle
    ├── Pricing.tsx                 ← €9 / 10 credits card
    ├── FAQ.tsx                     ← 8-question accordion
    ├── FinalCTA.tsx                ← closing CTA
    └── Footer.tsx
```

Read `globals.css` and `landing-components/AtsGauge.tsx` first — they contain the entire design language. Everything else is composition.

---

## 3. Design tokens

### 3.1 Palette — "Editorial Cream"

```css
/* Backgrounds */
--background:   #F5F0E6   /* bone — warm cream page bg */
--paper:        #FBF8F1   /* slightly lighter card bg */
--tan:          #E8DFD0   /* hairline borders, dividers */
--tan-soft:     #EFE7D6   /* subtle hover backgrounds */
--tan-dark:     #D9CDB8   /* stronger borders */

/* Ink (text) */
--ink:          #1A1612   /* primary text — deep warm black */
--ink-soft:     #3A322A   /* secondary text */
--stone-500:    #78716C   /* muted labels */
--stone-600:    #57534E   /* body copy */

/* Accents — used SPARINGLY. One accent per section, max. */
--oxblood:      #7A2828   /* primary accent — CTAs, key data, hover */
--oxblood-deep: #5C1D1D   /* hover state for oxblood */
--forest:       #3D7A4E   /* success — present keywords, high adherence */
--ochre:        #B8860B   /* warning — medium scores */
--brick:        #9B2C2C   /* danger — missing keywords, low scores */
```

**Rules:**
- Page background is always bone. Never use pure white (`#FFFFFF`) — it breaks the warmth.
- Borders are always `--tan` or `--tan-dark`. Never use pure gray.
- Oxblood is the ONLY accent for CTAs and key interactive elements. Do not introduce a second brand color.
- Forest/ochre/brick are reserved for semantic state (success/warning/danger) in data viz only.

### 3.2 Typography

```css
--font-display:  "Playfair Display", Georgia, serif;     /* all headings, gauge numbers */
--font-sans:     "Inter", system-ui, sans-serif;         /* body copy */
--font-mono:     "IBM Plex Mono", ui-monospace, monospace; /* badges, labels, IDs */
```

**Rules:**
- Playfair is the soul of this design. Use it for every heading (h1–h4) and every large numeric display. Never substitute.
- Italic Playfair = accent treatment for the second line of headlines (e.g. "Get the interview.").
- IBM Plex Mono is for ALL-CAPS labels with `letter-spacing: 0.15em–0.2em` (e.g. `STEP 5 / 7`, `ATS SCORE`, `MISSING`).
- Body copy is Inter at 16–18px with `line-height: 1.6–1.7`.

### 3.3 Spacing & radius

```css
--radius-sm:  4px;   /* tags, pills */
--radius:     8px;   /* cards, inputs */
--radius-lg:  12px;  /* hero card, dashboard mockup */
/* Do NOT use 16px+ radius. The look is print-document, not iOS. */
```

### 3.4 Shadows — soft, paper-like

```css
--shadow-paper:     0 1px 2px rgba(26,22,18,0.04), 0 8px 24px rgba(26,22,18,0.06);
--shadow-paper-lg:  0 2px 4px rgba(26,22,18,0.06), 0 16px 48px rgba(26,22,18,0.08);
/* Avoid neon glows. Avoid drop-shadow filters on UI chrome. */
```

### 3.5 Animations

| Name           | Duration | Easing                   | Use case                                |
|----------------|----------|--------------------------|-----------------------------------------|
| fade-up        | 0.7s     | `cubic-bezier(0.22,1,0.36,1)` | Scroll-triggered section reveals   |
| gauge-count    | 1.6s     | same                     | ATS score number counts up from 0       |
| aurora-drift   | 16s      | ease-in-out, infinite    | Background gradient blobs (very subtle) |
| marquee        | 32s      | linear, infinite         | Tech-stack ticker                       |
| pulse-soft     | 4s       | ease-in-out, infinite    | Status dots                             |
| float-y        | 6s       | ease-in-out, infinite    | Floating keyword badges                 |

**Rules:**
- Auroras on light bg must be VERY subtle — opacity 0.06–0.10. Anything stronger looks like a 2021 gradient hero.
- Hover states are immediate (150ms). Do not animate hover.
- Number count-ups are 1.6s with `cubic-bezier(0.22,1,0.36,1)`. Always animate from 0.

---

## 4. Component specs (Streamlit porting notes)

### 4.1 ATS Gauge (`AtsGauge.tsx`)

The hero element. SVG circle with:
- 60 tick marks around the perimeter (major every 5th)
- 12px stroke width on a 220px circle
- Color thresholds: ≥70 forest, 40–69 ochre, <40 brick
- Center: large Playfair number (32% of size), mono badge label below
- Animates the number from 0 → score over 1.6s when scrolled into view

**Streamlit port:** The repo already has `ui/dashboard.py` rendering a similar gauge. Update the colors to the palette above. Tick marks already exist in the original code — keep them.

### 4.2 Keyword tags

Two variants:
- **Present (forest):** `border: 1px solid rgba(61,122,78,0.3); background: rgba(61,122,78,0.1); color: #3D7A4E;`
- **Missing (brick):** `border: 1px solid rgba(155,44,44,0.3); background: rgba(155,44,44,0.1); color: #9B2C2C;`

Both use IBM Plex Mono, 11–12px, 6px border-radius, 4–8px padding. **Already exists in `ui/css.py` as `.keyword-tag-present` / `.keyword-tag-missing`** — just update the colors.

### 4.3 Section badges

Mono-font pills above every section heading:
- ALL-CAPS, `letter-spacing: 0.18em`, 11px
- Oxblood text on `rgba(122,40,40,0.05)` background
- `1px solid rgba(122,40,40,0.3)` border
- Pulsing 6px oxblood dot on the left

### 4.4 Cards

- Background: `--paper` (#FBF8F1)
- Border: `1px solid --tan` (#E8DFD0)
- Radius: 8px (NOT 16px)
- Shadow: `--shadow-paper`
- Hover: border darkens to `--tan-dark`, optional `-translate-y-0.5` lift

### 4.5 Primary button

- Background: oxblood (#7A2828)
- Text: paper (#FBF8F1), 14–16px, medium weight
- Hover: background darkens to `--oxblood-deep` (#5C1D1D)
- Radius: 8px
- **NO shimmer animation, NO glow shadow.** Just a solid color change.

---

## 5. Content (copy)

All headlines and CTAs are final — do not rewrite without explicit instruction.

- **Hero H1:** "Beat the bots. Get the interview." (line 2 italic oxblood)
- **Hero sub:** "cv2job scores your CV against any job description the way an ATS does — then rewrites it into a clean Harvard-format PDF that gets past the screeners. No invented experience. Just a sharper you."
- **Primary CTA:** "Optimize my CV — €9 / 10"
- **Secondary CTA:** "See the demo"
- **Section badges:** "ATS AI Resume Optimizer", "By the numbers", "The problem", "What's inside", "How it works", "Live ATS demo", "Pricing", "FAQ", "Ready when you are"
- **Pricing:** €9 for 10 optimizations, no subscription
- **Trust badges:** "No invented experience", "Harvard-format PDF", "Free ATS preview"

The full FAQ copy is in `landing-components/FAQ.tsx` — preserve verbatim.

---

## 6. Adaptation strategy

### Option A — Port tokens to Streamlit (RECOMMENDED)

**Why:** Your Streamlit app already has a sophisticated dark dashboard. The landing page now uses a light editorial palette. Bringing the two into alignment means updating `ui/css.py` to swap the dark theme for the editorial cream theme, while keeping the dashboard component structure intact.

**Steps for Codex:**

1. Open `ui/css.py`. Replace the CSS variables in `:root` with the palette in section 3.1 of this brief.
2. Update the dark-theme background (`#09090b`) to bone (`#F5F0E6`). Card backgrounds (`#18181b`) become paper (`#FBF8F1`).
3. The existing accent (`#818cf8`) becomes oxblood (`#7A2828`). Search-replace throughout `ui/css.py` and `ui/dashboard.py`.
4. Text colors flip: `#fafafa` → `#1A1612`, `#a1a1aa` → `#57534E`, `#52525b` → `#78716C`.
5. Keep the existing component structure (keyword tags, impact badges, sub-score circles, gauge). Only swap colors and shadows.
6. Remove `box-shadow: 0 4px 14px rgba(129,140,248,0.3)` glows — replace with `--shadow-paper`.
7. Add Google Fonts import for Playfair Display, Inter, IBM Plex Mono at the top of `ui/css.py` (Streamlit doesn't bundle these).
8. Update `ui/dashboard.py` gauge SVG: tick mark colors from `#3f3f46`/`#27272a` to `#b8a88e`/`#d9cdb8`. Track color from `#27272a` to `#e8dfd0`.
9. Test that the wizard, upload screen, results dashboard, and download screen all render correctly in the new palette. The Portuguese copy (`COM A VAGA`, `ENCONTRADOS`, `EM FALTA`, `PLANO DE ACÇÃO`) stays.

**Do NOT:**
- Change the Streamlit app structure, routing, or session state.
- Touch `api/`, `services/`, `pdf/`, or `tests/`.
- Add new dependencies.
- Re-implement the landing page inside Streamlit. The landing page is a separate Next.js deployment.

### Option B — Serve landing from FastAPI

**Why:** If you want everything under one backend, the landing page can be rendered as a static HTML template served by FastAPI. The Streamlit app stays at `/app`, the landing page at `/`.

**Steps for Codex:**

1. Convert the Next.js components to a single static HTML file using Tailwind CDN (or a pre-built CSS file).
2. Inline the critical CSS from `globals.css`. Strip the React-specific stuff.
3. Replace Framer Motion animations with CSS animations + `IntersectionObserver` for scroll triggers.
4. Add a Jinja2 template route to `api/main.py`: `GET /` returns the landing HTML, everything under `/api/*` stays as-is.
5. Keep the Streamlit app at its existing route (probably `/app` or via reverse proxy).
6. Update CTAs to point at the Streamlit app URL.

**This is more work and produces a worse result than Option A. Only do this if you have a strong reason to avoid a separate Next.js deployment.**

---

## 7. Acceptance criteria

After adaptation, verify:

- [ ] Page background is bone (#F5F0E6), not white, not dark.
- [ ] All headings render in Playfair Display (check the network tab — the font file is loading).
- [ ] ATS gauge colors match the thresholds (forest ≥70, ochre 40–69, brick <40).
- [ ] CTAs are solid oxblood with no glow.
- [ ] No pure gray borders anywhere — all borders are `--tan` or warmer.
- [ ] Keyword tags use the forest/brick colors, not the old emerald/red.
- [ ] No neon glows on any element.
- [ ] Mobile view (390px) renders without horizontal overflow.
- [ ] All Portuguese copy (`COM A VAGA`, `ENCONTRADOS`, `EM FALTA`, etc.) preserved.

---

## 8. What NOT to do

- Do not introduce a second brand color. One accent (oxblood) only.
- Do not use Tailwind's default `zinc` or `gray` palette. Use the warm stone/tan tokens above.
- Do not add gradient text. Use solid oxblood with italic for accent headlines.
- Do not add neon glows or `box-shadow` with color. Use `--shadow-paper` only.
- Do not change the radius scale. 8px max for cards.
- Do not replace Playfair Display with another serif. It's load-bearing.
- Do not add icon libraries beyond what's already imported (Lucide).
- Do not "improve" the copy. It's final.
