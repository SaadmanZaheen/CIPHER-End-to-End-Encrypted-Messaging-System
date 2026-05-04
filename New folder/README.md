# SecureConnect Design System

## Overview

**SecureConnect** is a secure, end-to-end encrypted social messaging web application built as a university cryptography project (CSE447, Spring 2026). It is a Flask + SQLite single-product web app that lets users register, create encrypted posts, and exchange private messages — all with custom-built RSA and ECC cryptography (no crypto libraries).

### Product
- **SecureConnect Web App** — A dark-themed, glassmorphism-inspired web UI built with Bootstrap 5.3 + custom CSS on top of Jinja2 templates. The single product surface. No mobile app; no marketing site; no docs.

### Sources
- **Codebase**: `447_Project/` (mounted via File System Access API — local path)
  - Entry: `447_Project/app.py`
  - Templates: `447_Project/templates/` (Jinja2 HTML, Bootstrap 5.3)
  - Styles: Inline in `447_Project/templates/base.html`
  - Routes: `447_Project/routes/auth.py`, `routes/posts.py`, `routes/social.py`
  - Crypto: `447_Project/crypto/` (rsa.py, ecc.py, hashing.py, mac.py)

---

## CONTENT FUNDAMENTALS

### Brand name & product name
- Product is called **SecureConnect** (used in navbar, page titles, brand copy)
- Older/partial references also use **SecureMsg** (legacy; found in some `<title>` tags)
- Canonical name to use going forward: **SecureConnect**

### Tone & voice
- **Functional, reassuring, security-forward.** The copy foregrounds encryption and trust, not social features.
- Not playful or emoji-heavy. Mostly serious — but not cold. Occasionally uses `🔒` as a literal security indicator (not decorative).
- First-person is rare; "you" is used for calls-to-action ("Your feed", "Your Network").
- Short, declarative phrases: "Create secure post", "Post securely", "Secure Channel".
- Feature names are capitalized when they reference security mechanisms: "E2E Encryption", "MAC Valid", "ECC", "RSA + ECC".

### Copy patterns
- **CTAs** are short imperatives: "Post securely", "Connect to Unlock", "Discover People", "Send Encrypted Message".
- **Empty states** use empathetic, soft language: "Your feed is quiet", "It's a bit lonely here", "No connections yet — build your network to start sharing securely."
- **Security badges** are terse technical labels: "MAC ✔", "ECC ✔", "Secure Channel", "End-to-End Encrypted", "ECDH Channel Key".
- **Error/success messages**: plain, brief flash messages. "Invalid credentials.", "Profile updated.", "Post created."
- **Nav labels**: Feed, My Posts, Discover, Messages, Network, Profile, Logout.

### Casing
- Title Case for nav items and section headers.
- Sentence case for body copy, form labels, and flash messages.
- ALL CAPS avoided except badge labels (e.g. "MAC", "ECC", "RSA").

### Emoji usage
- Used sparingly and only for security/lock metaphors: `🔒` in button labels ("Connect 🔒", "Add to Unlock 🔒").
- `💬` appears once for "Send Encrypted Message". Not a full emoji system — these are ad hoc.
- No decorative emoji in headings, cards, or navigation.

---

## VISUAL FOUNDATIONS

### Color system
- **Background**: Near-black zinc: `#09090b` (Tailwind zinc-950). Deep, not pure black.
- **Surface**: Dark zinc card: `#18181b` (Tailwind zinc-900). Used for cards, navbar.
- **Accent (primary)**: Purple `#8b5cf6` (Tailwind violet-500). Used for buttons, active states, primary CTAs.
- **Accent hover**: Deeper purple `#7c3aed` (Tailwind violet-600).
- **Gradient primary**: `linear-gradient(135deg, #a78bfa, #3b82f6)` — violet-400 → blue-500. Used for brand name, avatar backgrounds, some badges.
- **Text main**: `#f4f4f5` (zinc-100). Near-white.
- **Text muted**: `#a1a1aa` (zinc-400). Used for secondary copy, timestamps, labels.
- **Text placeholder**: `#71717a` (zinc-500).
- **Success**: `#34d399` (emerald-400) on `rgba(16,185,129,0.2)` bg + `rgba(16,185,129,0.3)` border. Used for MAC valid badge, "Connected" state.
- **Danger**: `#f87171` (red-400) on `rgba(239,68,68,0.2)` bg. Used for danger badges, Logout.
- **Info/Blue**: `#60a5fa` (blue-400) on `rgba(59,130,246,0.2)` bg. Used for info alerts and code highlights.
- **Warning/Gold**: `#facc15` (yellow-400) on `rgba(234,179,8,0.2)` bg. Used for Admin badge.
- **Primary glow**: `rgba(124,58,237,0.4)` — button drop-shadow glow.

### Typography
- **Font family**: `Inter` (Google Fonts), weights 300/400/500/600/700/800.
- **Brand / hero titles**: `fw-bold` (800), `letter-spacing: -1px`. e.g. "Your Feed", "Your Network".
- **Navbar brand**: 800 weight, 1.4rem, gradient fill (`#a78bfa → #3b82f6`), `letter-spacing: -0.5px`.
- **Body**: 400/500 weight, default size ~1rem. `line-height: 1.6` for post content.
- **Monospace**: Browser default monospace for crypto keys and ECDH previews (`<code>`).
- **Badges / labels**: 600 weight, `letter-spacing: 0.5px`, small (0.75rem for badge-mac).
- **Anti-aliasing**: `-webkit-font-smoothing: antialiased`.

### Spacing & layout
- Max content width: `900px` (`container`).
- Page padding: `padding-top: 2rem`, `padding-bottom: 4rem`.
- Card `padding`: `1.5rem` body, `1.25rem 1.5rem` header.
- Gaps between elements use Bootstrap grid + `gap-2` / `gap-3` utilities.

### Cards
- `border-radius: 20px` (rounded-4 equivalent).
- `border: 1px solid rgba(255,255,255,0.05)` — extremely subtle.
- `background: #18181b` (surface-dark).
- `box-shadow: 0 10px 30px rgba(0,0,0,0.2)`.
- Hover: `translateY(-2px)` + `box-shadow: 0 15px 35px rgba(0,0,0,0.3)`.
- Special post cards get accent border: `1px solid rgba(139,92,246,0.3)` + `box-shadow: 0 0 20px rgba(139,92,246,0.1)`.
- `overflow: hidden` on all cards.

### Buttons
- **Primary**: `linear-gradient(135deg, #8b5cf6, #3b82f6)`, `border-radius: 12px`, `font-weight: 600`, glow shadow `rgba(124,58,237,0.4)`.
- Hover: deeper gradient, `translateY(-2px)`, stronger glow.
- **Outline primary**: `border: 2px solid #8b5cf6`, `color: #8b5cf6`, `border-radius: 12px`, fill on hover.
- **Pill variant**: `border-radius: 9999px` (rounded-pill) used for secondary actions like "Post securely", "Discover".
- **Small actions**: `border-radius: 12px`, custom background colors from semantic palette.

### Form inputs
- Background: `rgba(255,255,255,0.03)`.
- Border: `1px solid rgba(255,255,255,0.08)`.
- `border-radius: 12px`, padding `0.75rem 1rem`.
- Focus: border turns `#8b5cf6`, box-shadow `0 0 0 4px rgba(139,92,246,0.15)`.
- Placeholder: `#71717a`.

### Navbar
- Glassmorphism: `background: rgba(24,24,27,0.7)`, `backdrop-filter: blur(12px)`.
- `border-bottom: 1px solid rgba(255,255,255,0.05)`.
- Sticky top, `z-index: 1000`.
- Nav links: muted by default, hover → white + `rgba(255,255,255,0.05)` bg + `translateY(-1px)`.

### Badges
- `border-radius: 8px`, padding `0.5em 0.8em`, `font-weight: 600`.
- All semantic badges use translucent colored backgrounds with matching border.
- Security status badges ("MAC", "ECC") are small (`badge-mac`, 0.75rem) with inline SVG icons.

### Backgrounds & textures
- Flat dark backgrounds only — no images, no patterns, no textures.
- No gradients on backgrounds (only on buttons and the brand logotype gradient).
- `data-bs-theme="dark"` on `<html>` — Bootstrap dark mode baseline.

### Animations
- Single `fadeIn` keyframe: `opacity: 0 → 1`, `translateY(15px → 0)`, `0.5s ease`.
- Applied via `.fade-in` class with staggered `animation-delay` on page load elements.
- Transition shorthand on interactive elements: `all 0.3s ease`.
- No bounces, no spring animations, no complex sequences. Subtle and functional.

### Glassmorphism
- Used on navbar and locked-post overlay: `backdrop-filter: blur(12px)`, semi-transparent background, subtle border.
- Applied sparingly — only on floating/overlay surfaces.

### Avatars
- Circular letter-avatars: user's first letter, uppercase, centered in a circle.
- **Own/primary**: `background: linear-gradient(135deg, #a78bfa, #3b82f6)`, white text.
- **Others**: `background: linear-gradient(135deg, #4b5563, #1f2937)`, white text.
- Sizes: 40×40px (feed/nav), 48×48px (network list), 72×72px (discover cards).

### Shadows & elevation
- Cards: `box-shadow: 0 10px 30px rgba(0,0,0,0.2)`.
- Hover cards: `box-shadow: 0 15px 35px rgba(0,0,0,0.3)`.
- Buttons: `box-shadow: 0 4px 15px rgba(124,58,237,0.4)`.
- No heavy shadows; elevation is communicated by `rgba(0,0,0)` alpha, not color.

### Corner radii
- Cards: `20px`.
- Buttons (default): `12px`.
- Buttons (pill): `9999px`.
- Badges: `8px`.
- Inputs: `12px`.
- Alerts: `12px`.
- Avatars: `50%` (circle).

### Color vibe of imagery
- No photography used. All content is text-based.
- The one external image is a QR code (for OTP setup), served from `api.qrserver.com`.

### Use of transparency and blur
- Glassmorphism on navbar and locked-post overlays.
- Card backgrounds are semi-transparent `rgba(24,24,27,0.X)` when layered on the dark page bg.
- Locked post content uses `filter: blur(5px–8px)` to obscure text visually.

### Hover & press states
- Hover: `translateY(-2px)` lift + `box-shadow` increase. Color deepens on buttons.
- Nav hover: slight white background tint + white text color.
- List items: `background` transitions from transparent to `rgba(255,255,255,0.03)`.
- No shrink/scale press state; no ripple effect.

---

## ICONOGRAPHY

SecureConnect uses **inline SVG icons** exclusively — no icon font, no PNG icons, no external icon CDN. Icons are hand-authored directly in HTML templates.

### Icon style
- Stroke-based (line icons), `stroke-width: 2–2.5`.
- `stroke-linecap: round`, `stroke-linejoin: round`.
- `fill: none`.
- Style is consistent with **Lucide Icons** or **Feather Icons** aesthetics (thin, rounded stroke).
- Colors: inherit from `currentColor` or use the gradient defs inline.

### Usage
- **Brand logo (navbar)**: Lock icon — padlock body + shackle (`rect` + `path`).
- **Feed locked state**: Lock icon (same padlock motif), 32×32px, `stroke: currentColor`.
- **Security badges**: Tiny 12×12 inline SVGs — checkmark (`polyline`) for MAC ✔; shield (`path`) for ECC ✔.
- **Network/friends empty state**: Users/group icon (`path`, `circle`).

### No icon assets to copy
There is no icon font, sprite sheet, or SVG file — all icons are inline in template HTML. When using this design system, replicate the inline SVG patterns above. The Lucide icon set (available at `https://unpkg.com/lucide@latest`) is the best CDN match for the icon style used.

### Key SVG patterns used
```html
<!-- Lock (brand logo / locked state) -->
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
</svg>

<!-- Shield (ECC badge) -->
<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
</svg>

<!-- Checkmark (MAC badge) -->
<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="20 6 9 17 4 12"></polyline>
</svg>
```

---

## FILES IN THIS DESIGN SYSTEM

```
README.md                       ← This file (brand overview, content fundamentals, visual foundations, iconography)
SKILL.md                        ← Agent skill definition for Claude Code
colors_and_type.css             ← CSS custom properties for colors, typography, spacing, radii, shadows

preview/                        ← Design system card previews (visible in Design System tab)
  colors-base.html              ← Base color swatches (bg, surface, text, accent, blue)
  colors-semantic.html          ← Semantic color chips (success, danger, info, warning, primary)
  colors-gradients.html         ← Gradient swatches (brand, button, hover, avatar)
  type-scale.html               ← Full type ramp 3xl/800 → xs/600
  type-specimens.html           ← Brand text, nav links, post body, monospace crypto text
  spacing-tokens.html           ← Bar chart of spacing tokens 4px → 64px
  shadows-radii.html            ← Shadow elevations + corner radius tokens
  buttons.html                  ← All button variants (primary, outline, pill, sm, success, danger, disabled)
  badges.html                   ← All badge variants (MAC, ECC, Secure Channel, semantic, pill)
  form-inputs.html              ← Text/password/textarea inputs with states + E2E toggle
  cards.html                    ← Post card, discover card, empty state card
  avatars.html                  ← Letter-avatar sizes and styles (own/other)
  navbar.html                   ← Glassmorphism sticky navbar
  feed-post-card.html           ← Compose card with encryption toggle
  locked-post.html              ← Blurred encrypted post with glassmorphism unlock overlay
  brand-logo.html               ← Lock icon + wordmark in large and small sizes

ui_kits/
  web/
    README.md                   ← UI kit usage notes
    index.html                  ← Interactive click-thru prototype (open this!)
    NavBar.jsx                  ← Glassmorphism sticky navbar component
    AuthScreens.jsx             ← Login, Register, OTP Setup, OTP Verify
    FeedScreen.jsx              ← Feed with compose card, post cards, locked posts
    MessagesScreen.jsx          ← Inbox list + conversation / chat view
    NetworkScreen.jsx           ← Network (friends list) + Discover people grid
    ProfileScreen.jsx           ← Profile details + Key Rotation screen
```

### How to use this design system
1. Read this README for brand rules (colors, type, tone, iconography).
2. Import `colors_and_type.css` for CSS variables in any HTML prototype.
3. Open `ui_kits/web/index.html` for a full interactive prototype of the app.
4. Copy individual `preview/` cards for reference on specific components.
5. All icons are inline SVG — no external icon dependency required (Lucide-style, stroke-based).
