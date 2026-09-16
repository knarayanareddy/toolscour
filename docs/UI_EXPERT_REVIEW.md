# AI ToolScour — Multi-Agent Expert UI Review (v1 → v2)

Five expert personas audited the v1 interface against 2026 design research on
AI-generated-UI convergence ("AI slop") and best-in-class dev-tool systems
(Linear, Raycast, Vercel). Verdicts below; every finding has a shipped fix.

---

## Research base

- **The convergence loop**: LLMs emit the statistical median of training data.
  Tailwind shipped `indigo-500` as default in 2019; it became the most common
  button color in scraped code, so every agent now "designs" violet. Tailwind's
  creator publicly apologized for it (Adam Wathan, 2025).
- **The tells**: Inter/system fonts, blue→purple gradients, gradient wordmarks,
  uniform `rounded-2xl` gray-bordered cards, backdrop-blur glassmorphism,
  3-card grids, drop shadows everywhere. Any one reads as machine-made.
- **The fix pattern** (Linear / Raycast / Vercel): commit to ONE direction and
  lock tokens; 1 dominant accent + restraint; hairline borders instead of
  shadows; tight radius vocabulary; mono for machine data; display face with
  actual character; APCA-measured contrast.

---

## Persona verdicts

### 1. Nova Reyes — Brand & Visual Identity Strategist
> "Your wordmark is a violet gradient, your CTAs are violet, your tab pills are
> violet-to-fuchsia. This is the single most recognizable AI-generated pattern
> of 2025–2026. Swap the logo with any other AI directory and nobody notices."

**Findings**
- Violet/fuchsia everywhere = training-corpus median, not a decision.
- `bg-clip-text` gradient wordmark is a top-3 slop tell.
- No ownable asset: the 10-sector spectrum — the product's most distinctive
  property — was invisible in chrome.

**Shipped fixes**
- New identity: **Stellar Catalog** (observatory concept; every tool is a
  catalogued object). Locked in `docs/DESIGN.md`.
- Single dominant accent **starlight gold `#f2b13d`** — semantically loaded:
  the star is literally the product's ranking unit.
- Display face **Bricolage Grotesque** + body **Instrument Sans** + machine
  data in **JetBrains Mono**. Inter banned.
- All gradient text/buttons removed; solid-gold CTA with ink text.

### 2. Dr. Amara Osei — UX Researcher
> "The cards are rhythmically identical, so nothing earns a second look. The
> domain chip — the most decision-relevant attribute — was the same color as
> every other chip. Users filter by sector, but the interface hides it."

**Findings**
- Uniform card rhythm → flat scan path, no landmark moments.
- Domain (sector) is the primary IA axis yet was visually undifferentiated.
- Glassmorphism blur adds perceptual noise without information.
- No object identity: tools read as a list, not a catalogue.

**Shipped fixes**
- **Spectral domain chips**: each of the 10 sectors now carries its data hue
  on chips in cards and the inspector — the IA becomes scannable at a glance.
- **OBJ·{id} telemetry tags** give every card catalog identity.
- Mono uppercase micro-labels create scan rhythm; one orchestrated entrance
  animation (`rise-in`) replaces scattered motion.
- `backdrop-blur` removed from chrome (kept only on the sticky header).

### 3. Kai Lindqvist — Design Systems Lead
> "There were no tokens. Eleven accent hues, two radius habits, and elevation
> built from shadows *and* borders *and* blur at once. That's three elevation
> systems doing one job."

**Findings**
- No DESIGN.md → every component re-decided its styling (root cause of slop).
- Radius vocabulary inconsistent (`rounded-xl` vs `2xl` with no rule).
- Shadows + borders + blur stacked redundantly.

**Shipped fixes**
- `docs/DESIGN.md` locks palette, type, radius, motion, and explicit Don'ts.
- Tailwind config now encodes tokens: `ink` surface ladder, `star`/`ion`
  accents, radius scale **6 / 10 / 14**, display/sans/mono font families.
- Elevation reduced to hairline borders; card shadows deleted.

### 4. Priya Raman — Accessibility Lead
> "Measured against APCA on dark: your micro-labels sat at the edge, focus
> states were browser-default blue (and inconsistent), and gold-on-dark was
> your only reliably strong pairing — which you barely used."

**Findings**
- Default focus rings broke the dark theme's contrast contract.
- Motion was scattered (multiple independent animations = vestibular load).

**Shipped fixes**
- Global gold `:focus-visible` ring, consistent across inputs/buttons.
- Weakest body copy lifted (slate-600 → slate-500 for readable text).
- Solid gold CTA with `#171204` ink text — Lc well above 75.
- Motion consolidated: one staggered entrance, hover ticks, canvas physics.

### 5. Marcus Vale — Data Visualization Specialist
> "You have ten spectral bands for ten AI sectors and you only showed them
> inside the canvas. Bring the spectrum into the catalog or the galaxy feels
> like a different product than the list."

**Findings**
- Domain colors existed only in `Graph3DExplorer`'s `DOMAIN_CONFIG`.
- Chrome accents (indigo) competed with data colors inside the 3D view.

**Shipped fixes**
- Single source of truth: `DOMAIN_COLORS` in App.jsx mirrors the canvas map;
  chips, dots, and nodes now share one spectrum.
- 3D chrome recolor to **ion teal** — telemetry color, clearly distinct from
  the gold brand CTA and from data hues.

---

## Slop-tell scorecard (before → after)

| Tell                                   | v1 | v2 |
|----------------------------------------|----|----|
| Violet/indigo primary + gradients      | ❌  | ✅ eliminated |
| Gradient wordmark                      | ❌  | ✅ solid display face |
| Inter / system-stack type              | ❌  | ✅ Bricolage + Instrument + JetBrains Mono |
| Uniform rounded gray-bordered cards    | ❌  | ✅ 3-step radii, hairlines, hover corner ticks |
| Backdrop-blur glassmorphism            | ❌  | ✅ removed from chrome |
| Drop shadows for elevation             | ❌  | ✅ borders only |
| Palette > 3 active hues on chrome      | ❌  | ✅ gold + ion + neutrals (spectrum = data only) |
| Locked design tokens (DESIGN.md)       | ❌  | ✅ docs/DESIGN.md + tailwind tokens |
| Object/data identity in chrome         | ❌  | ✅ OBJ ids, spectral chips, mono telemetry |

---

# Round 2 — Auditing v2 itself (the harder review)

The panel reconvened after v2 (gold-on-dark "Stellar Catalog") shipped, with a
mandate to attack their own work. Research updated the threat model: dark mode
is now *standard* (Figma 2026 trends), and ~75% of design-led dev-tool SaaS
already runs "dark-by-default + one neon accent" — Linear-purple, Raycast-red,
Mercury-lime, Cursor-cyan. Gold-on-dark with mono telemetry is the 2026
*second-generation* AI/dev-tool cliché.

## Verdicts

### Nova Reyes — Brand Strategist
> "We escaped the purple median only to land on the other median. Near-black +
> single neon + mono micro-labels is what every agent ships now. Nobody will
> screenshot this and remember it."
>
> **Prescription:** invert the category. Every AI directory is dark. A star
> catalog's real heritage is PRINT — Uranometria, Flamsteed, celestial
> almanacs. Ivory paper, ink, gold leaf, engraved rules. Go light.

### Dr. Amara Osei — UX Researcher
> "Dark-on-dark hierarchies flatten at distance; on paper, hairline borders and
> ink weights do the work with zero glow. And the 3D galaxy becomes a *moment*
> instead of a wallpaper — a dark viewport you look INTO, framed by paper."

### Kai Lindqvist — Design Systems Lead
> "Tokens updated: `paper` surface ladder (50/100/200/300/400), gold split into
> `star-500` surface gold vs `star-700` gold-ink for text on paper, serif
> display tier added. Exceptions are explicit and enumerated — exceptions a
> system can't name are how slop creeps back in."

### Priya Raman — Accessibility Lead
> "APCA improves materially: stone-900 body on ivory (Lc ~ -90), gold-ink
> #a3690d on #fffdf7 passes comfortably for text and icons. Light mode also
> broadens the audience — astigmatism-friendly, daylight-readable."

### Marcus Vale — DataViz Specialist
> "Keep the spectrum identical across paper chrome and dark canvas — hue
> continuity is what makes the telescope feel like the same product. Dark
> canvases are now *fewer and more deliberate*, which makes them stronger."

## Shipped as v3 — "Paper Atlas"

| Move | Detail |
|------|--------|
| Inversion | Chrome → warm ivory paper (`#f7f3e8` ladder); dark mode deleted from chrome |
| Telescope viewports | Graph3DExplorer + Stack3DVisualizer stay deep-space dark, framed by paper — the concept's hero moment |
| Type | Display → **Fraunces** serif (plate-atlas character); Instrument Sans body; JetBrains Mono telemetry |
| Gold split | `star-500` for solid CTA surfaces; `star-700` gold-ink for text/icons/focus/ticks |
| Atlas framing | Double rules under header / above footer; OBJ·id tags; spectral chips |
| Terminal ink | CLI quickstart blocks remain dark stamps on paper |
| Slop audit | 0 violet/indigo/fuchsia, 0 gradient text, 0 Inter; dark surfaces exist in exactly 2 sanctioned files |

---

# Round 3 — The forensic pass ("it still looks purple")

The user reported purple a third time. The panel stopped theorizing and
audited every rendered pixel source. Chrome was clean — the leak was in the
**data layer**:

1. **Foundation Models & Weights was encoded `#c084fc` — violet — and that
   sector is 61% of the entire corpus** (6,477 of 10,635 tools). Every chip,
   dot, and galaxy node there rendered violet. The product was purple because
   the *data* was purple.
2. Stack3DVisualizer's Layer-2 node color was the same violet.
3. Spectrum collision defects: Agents' amber ≈ brand gold; CodeGen's green ≈
   Inference's emerald; Edge's cyan ≈ RAG's sky; Robotics' orange ≈ Agents'
   amber — data hues were indistinguishable from each other and from chrome.

## Shipped fix (Spectrum v4)

- Full 10-hue retune across `App.jsx`, `Graph3DExplorer.jsx`,
  `Stack3DVisualizer.jsx` — single source of truth mirrored in all three.
- **Violet band (265°–330°) permanently banned** from the data spectrum;
  Foundation Models moved to cobalt `#3b5bdb`.
- Collision pairs resolved (amber↔gold, green↔emerald, cyan↔sky, orange pairs).
- Bundle audit: **0 violet-family hex values** in the shipped JS/CSS.

> Marcus Vale (DataViz): "When one category owns 60% of your records, its hue
> IS your brand color whether you like it or not. We were shipping a violet
> brand with gold trim. Now cobalt carries the mass, and no sector color can
> be mistaken for chrome again."
