# AI ToolScour — Locked Design System ("Paper Atlas", v3)

> This file is the authority on visual decisions. Do not reintroduce violet,
> indigo, fuchsia, Inter, gradient wordmarks, backdrop-blur chrome, or
> dark-mode-by-default. Root-cause of the v1 look: statistical-average defaults
> ("AI slop"). Root-cause risk of v2: "dark + one neon accent" became the
> 2026 dev-tool cliché itself (Figma trends: dark mode is now *standard*).

## 1. Concept

**The catalog is paper; the telescope is night.** Star atlases are a print
tradition — ivory paper, ink, gold leaf, engraved rules. The chrome of
AI ToolScour is a paper atlas: warm ivory surfaces, stone ink typography,
gold-ink accents, serif display, double rules, plate-style labels. The two
3D canvases (galaxy explorer, stack constellation) are the EXCEPTION —
dark telescope viewports embedded in the paper, the only night sky in the
product. Inverting dark-mode-by-default is the deliberate anti-cliche move.

## 2. Palette (capped: 1 dominant + 1 support + data spectrum + neutral ramp)

| Token        | Value     | Use                                                        |
|--------------|-----------|------------------------------------------------------------|
| `paper-100`  | `#f7f3e8` | Page canvas (warm ivory)                                    |
| `paper-50`   | `#fffdf7` | Cards, raised surfaces                                      |
| `paper-200`  | `#efe9d8` | Wells, inputs, insets                                       |
| `paper-300/400` | `#e0d8c2 / #c9bea2` | Hairline borders / strong borders             |
| `star-500`   | `#f2b13d` | **The only primary** as solid surfaces (CTAs, active tabs) with ink text `#171204`. |
| `star-700`   | `#a3690d` | Gold as INK on paper: text, icons, focus rings, corner ticks. Star counts share it — the star is the product's unit. |
| `ion`        | `#4cc9b8` | Telemetry accent inside dark canvases ONLY.                 |
| text         | stone ramp| Body `stone-800/900`, secondary `stone-600`, micro `stone-500` |
| spectrum     | 10 hues   | One hue per AI domain — **data color only** (chips, dots, 3D nodes). Never decoration. **v4 retune: zero violet anywhere** (Foundation Models moved cobalt `#3b5bdb`; violet had colonized 61% of the corpus). Hues de-collided: no amber-vs-gold, green-vs-emerald, or cyan-vs-sky pairs. |
| terminal ink | `#101317` | CLI quickstart blocks: dark ink stamps on paper.            |

Rules:
- No gradient text, no gradient buttons. Gradients exist only inside the 3D canvas vignette.
- No drop shadows on cards — hairline borders (`slate-800`) do elevation.
- One chromatic CTA style: solid `star-500` bg, ink text (`#171204`).
- APCA targets on dark: body ≥ Lc 75, large/bold ≥ 45, icons/borders ≥ 30.

## 3. Typography

| Role       | Face                  | Rules                                            |
|------------|-----------------------|--------------------------------------------------|
| Display    | **Bricolage Grotesque** | Wordmark + section headers. Tight tracking, weight ≤ 800. |
| Body / UI  | **Instrument Sans**   | Everything readable. Weights 400–600.            |
| Machine    | **JetBrains Mono**    | Catalog IDs, stats, chips, CLI, filters, telemetry. Mono says "this is a tool." |

Inter, Roboto, and Space Grotesk are banned (training-corpus convergence tells).

## 4. Radius & Borders (three-step vocabulary, Linear/Raycast discipline)

- Buttons / inputs / inline chips: **6px**
- Cards: **10px**
- Modal / hero panels: **14px**
- Pills: `9999px` only for true pills
- Hairline `1px` borders; no `backdrop-blur` on cards (header bar only).

## 5. Signature details (the anti-generic layer)

1. **Object IDs** — every card carries a mono `OBJ·{id}` telemetry tag.
2. **Spectral domain dots** — domain chips carry their sector's data hue.
3. **Mono micro-labels** — `10px`, uppercase, `tracking-[0.14em]`, stone-500.
4. **Corner ticks** on card hover (gold ink), gold-ink focus rings.
5. **Double rules** (border-double, 4px) under the header and above the
   footer — engraved atlas framing.
6. **Telescope viewports** — the two 3D canvases stay deep-space dark, framed
   by paper chrome. This contrast IS the concept; do not "harmonize" it.
7. **Terminal ink stamps** — CLI quickstart blocks stay dark on paper.
8. One orchestrated motion moment: card rise-in + tick reveal. No scattered
   micro-animation confetti.

## 6. Don't

- Don't add violet/indigo/fuchsia or blue→purple gradients anywhere.
- Don't revert to dark-mode-by-default chrome (dark = telescope viewports only).
- Don't add drop shadows to separate surfaces.
- Don't widen the palette beyond the table above.
- Don't use radii > 14px except pills.
- Don't use chromatic text for body copy.

## 7. Spectral Data Palette v4 (locked)

| Sector | Hue |
|---|---|
| Foundation Models & Weights | `#3b5bdb` cobalt |
| Local Inference & Serving | `#0ca678` teal-green |
| Agentic Frameworks & Swarms | `#e03131` vermillion |
| Vector DBs & RAG | `#1098ad` deep cyan |
| Fine-Tuning & Alignment | `#c2255c` berry |
| Dev Tooling & Evals | `#66a80f` olive |
| Code Generation & IDE | `#2b8a3e` forest |
| Synthetic Media & Audio | `#e64980` pink |
| Robotics & Embodied | `#e8590c` burnt orange |
| Edge & Embedded | `#7f5539` earth brown |

Rules: purple/violet band (265°–330°) is permanently banned from the data
spectrum; every hue must be distinguishable from brand gold `#f2b13d` at
chip size on ivory.
