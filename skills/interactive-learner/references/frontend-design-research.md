# How to Design a Great Learning Frontend

Comprehensive research summary — February 2026

---

## 1. Learning UX Design Principles

### The Science Foundation

Effective learning interfaces are grounded in two convergent bodies of research:

**Cognitive Load Theory (Sweller)** — Working memory is the bottleneck. Every design decision either wastes cognitive capacity (extraneous load), reflects inherent topic difficulty (intrinsic load), or supports genuine understanding (germane load). The entire job of a learning frontend is to minimize the first, manage the second, and maximize the third.

**Multimedia Learning Theory (Mayer)** — Empirically validated principles with measured effect sizes:

| Principle | Effect Size (d) | Design Rule |
|---|---|---|
| Multimedia | 1.67 | Words + graphics together, never words alone |
| Temporal Contiguity | 1.30 | Present related text and visuals simultaneously |
| Spatial Contiguity | 0.79 | Place text near corresponding graphic |
| Redundancy | 0.87 | Don't duplicate on-screen narration as text |
| Coherence | 0.70 | Remove every non-essential element |
| Modality | 0.72 | Use narration + visuals, not on-screen text + visuals |
| Signaling | 0.46 | Highlight, cue, and direct attention to key info |

These effect sizes are large — implementing even a few of these principles produces measurable learning gains.

### Core UX Principles for Learning Interfaces

1. **Every pixel serves learning.** Decorative elements that don't aid comprehension create extraneous load. Beautiful ≠ busy. The best learning UIs feel spacious and calm.

2. **Active over passive.** Interfaces that require the learner to *do* something (predict, choose, build, explain) outperform passive reading/watching. Execute Program's key insight: text "unfurls" only after the learner completes an interactive prompt, making passive scrolling impossible.

3. **Immediate, specific feedback.** Response within 200ms feels instant. Feedback must be specific ("Pods wrap containers, not replace them") not generic ("Try again"). Include *why* the answer is right or wrong.

4. **Progressive complexity.** Start concrete, ascend to abstract. Reveal advanced UI/features only as competence grows. Layered interfaces measurably reduce training time (Open University, 2025).

5. **Personalization and adaptivity.** Track mastery, predict optimal next steps, adapt practice frequency. But — critical finding from Frontiers 2025 — adaptive features must be *discoverable and integrated* into the core learning loop, not hidden in settings.

6. **Consistency and predictability.** Learners shouldn't spend cognitive effort figuring out the UI. Consistent patterns, predictable interactions, stable layouts free working memory for content.

---

## 2. Interaction Design for Learning

### Interaction Patterns Ranked by Learning Depth

**Recall / Recognition (Low cognitive demand)**
- Multiple choice questions with feedback
- True/false with explanation
- Click-to-reveal definitions
- Flashcard flip interactions

**Application / Analysis (Medium cognitive demand)**
- Fill-in-the-blank with drag-and-drop choices
- Matching pairs (connect term to definition)
- Sorting/ordering (arrange steps, rank items)
- Code completion with live execution

**Synthesis / Evaluation (High cognitive demand)**
- Branching scenarios and case studies
- Simulators with manipulable variables
- Build-from-scratch exercises (configs, code, diagrams)
- Sandbox/playground with open-ended exploration

### Key Interaction Design Principles

**Align interaction to learning verb.** Before picking a widget, identify the cognitive action: recognize, apply, compare, evaluate, create. Then choose the lightest-weight interaction that demands that action.

**Purposeful clicks only.** Every click should require thinking. If a learner can succeed by random clicking, the interaction isn't teaching. (Hick's Law applies — don't overwhelm with options either.)

**Balance guidance vs. exploration.** PACIS 2025 field experiment finding: interactive features increase exploration and long-term technique adoption, but *excessive guidance suppresses exploration and reduces learning benefit*. The sweet spot is structured freedom — clear guardrails, but room to experiment.

**Chunk and scaffold.** Use tabs, accordions, click-to-reveal, and step-by-step progression to break complex content into digestible pieces. Don't show everything at once.

### The "Explorable Explanations" Model (Bret Victor / Nicky Case)

The gold standard for interactive learning content:

- **Reactive documents**: Readers tweak assumptions/parameters and see immediate consequences. Not "read then quiz" — the reading IS interactive.
- **Do → Show → Tell**: Use interactivity only when it outperforms text or static graphics. Text for abstract ideas, graphs for relationships, animation for temporal processes, interactives for systems/models.
- **Interest curve**: Hook (low-barrier interactive opener) → Build (ascending abstraction) → Conclude (sandbox or synthesis that leverages everything learned).
- **Ladder of abstraction**: Start grounded in concrete examples, ascend slowly to general concepts. Never open with jargon.
- **Start with "?"**: Open with a compelling question that motivates exploration.

---

## 3. Visual Design for Education

### Typography

Research-backed specifications for learning content:

| Property | Recommendation | Source |
|---|---|---|
| Body font size | 16–18px minimum on web | Readability Consortium, Typography Guide 2025 |
| Line height | 1.5–1.72× font size | Best practice + current shell.html value |
| Line length | 50–75 characters (max 740px container) | Readability research |
| Font family | Simple, open-counter, wide letterforms, large x-height | Perceptual science review 2025 |
| Heading font | Heavier weight, tighter letter-spacing for contrast | Typographic hierarchy practice |
| Code font | Monospace with ligature support (JetBrains Mono, Fira Code) | Developer education standard |
| Letter spacing | Slightly increased for body; especially helpful for accessibility | Readability Matters classroom evidence |
| Alignment | Left-aligned body text (never justified on web) | Readability research |

**Personalizable typography matters.** A K-8 study (n=94) found children have a stable "personal best" text format — allowing adjustment of font size, spacing, and line height measurably improved comprehension.

**Recommendation for the shell:** The current shell.html uses DM Sans (body) + Outfit (headings) + JetBrains Mono (code) — all excellent choices. DM Sans has open counters and good weight range. Outfit provides bold, distinctive headings. Consider adding user controls for font size and letter spacing.

### Color

**Research findings (2025–2026):**
- Content-relevant, moderate color cues improve retention and transfer (video lecture eye-tracking study). Excessive color raises cognitive load.
- Light background + dark text is generally more readable. Background color alone is not a meaningful retrieval cue — it's stored as context, not content.
- Color should *support* information hierarchy, not replace it. Never use color as the sole indicator of status (accessibility).

**Color system for learning:**

```
Primary palette:
- Background: dark (#111114) or light (#fafafa) — user choice
- Content surface: slightly raised (#1a1a20 dark / #ffffff light)
- Primary accent: used sparingly for interactive elements, progress, active states
- Semantic colors:
  - Green: correct, success, complete
  - Red/coral: incorrect, error (never harsh — use muted tones)
  - Orange/amber: warning, hints, XP/rewards
  - Cyan/blue: information, links, code highlights
  - Purple: accent, mastery, premium feel

Design rules:
- Max 3 colors visible at any moment
- 60% neutral / 30% secondary / 10% accent
- WCAG AA minimum: 4.5:1 contrast ratio for body text
- WCAG AAA target: 7:1 for small text in learning contexts
```

### Layout and Information Hierarchy

**Single-column, vertical scroll is king for learning.** Multi-column layouts split attention. The current 740px max-width container is research-aligned.

**Hierarchy techniques that work:**
1. **Size contrast** — Headings significantly larger than body
2. **Weight contrast** — Bold key terms within normal-weight text
3. **Spatial grouping** — Related items close together, unrelated items separated by whitespace
4. **Color accent** — Sparingly highlight the one thing to focus on
5. **Progressive reveal** — Show only the current focus; dim/hide the rest
6. **Border/card treatment** — Elevate interactive components from narrative text

**The "one thing per screen" principle:** Each viewport-height section should have one primary focus. If a learner has to choose between multiple competing elements, you've overloaded the screen.

---

## 4. Accessibility in Learning Platforms

### Standards Framework (2025–2026)

- **WCAG 3.0** is the next-generation standard (Working Draft Sept 2025, Editor's Draft Feb 2026). Covers web, mobile, wearable, VR/AR.
- **ATAG** (Authoring Tool Accessibility Guidelines) — applies to lesson authoring tools and content creation workflows.
- **UK DfE Accessibility Manual** — gold standard for education-specific accessibility standards, audits, and testing.

### Non-Negotiable Accessibility Requirements

1. **Keyboard navigation** — Every interactive element must be fully operable via keyboard. Tab order must be logical. Focus states must be clearly visible.

2. **Screen reader support** — All images need alt text. Interactive components need ARIA labels, roles, and live regions for dynamic updates. Quiz feedback must be announced.

3. **Color contrast** — 4.5:1 minimum for normal text, 3:1 for large text. Never use color alone to convey information (add icons, text labels, or patterns).

4. **Reduced motion** — Respect `prefers-reduced-motion`. All animations must have a reduced/no-motion alternative. This includes confetti, shake effects, slide-in reveals.

5. **Text scaling** — UI must remain functional at 200% zoom. Use relative units (rem, em, %) not fixed px for text.

6. **Focus management** — When content dynamically appears (quiz feedback, revealed sections), move focus appropriately so assistive technology users aren't lost.

7. **Captions and transcripts** — Video content requires captions. Audio explanations need transcripts.

### Khan Academy's Accessibility Innovation (2025)

Khan Academy rebuilt their graphing components using the Mafs library specifically for accessibility — adding full keyboard navigation, screen reader descriptions, and high-contrast mode to math visualizations. This is the benchmark: interactive visualizations that work for everyone.

### Actionable Checklist

```
[ ] Tab through entire lesson without mouse — everything reachable?
[ ] Screen reader announces all content and state changes?
[ ] Color contrast passes WCAG AA (4.5:1) everywhere?
[ ] prefers-reduced-motion disables all animations?
[ ] Text scales to 200% without breaking layout?
[ ] Focus indicators visible on every interactive element?
[ ] No information conveyed by color alone?
[ ] All images have descriptive alt text?
[ ] Dynamic content changes announced to assistive tech?
[ ] Touch targets minimum 44x44px on mobile?
```

---

## 5. Mobile-First and Responsive Design

### Mobile-First Is the Correct Approach for Learning

Most informal learning happens on phones — commuting, waiting, short study sessions. Design for the constrained case first, then enhance.

### Implementation Strategy

**Responsive breakpoints (content-driven, not device-driven):**

```css
/* Mobile-first base: < 640px */
.container { padding: 16px; max-width: 100%; }

/* Tablet: 640px+ */
@media (min-width: 640px) {
  .container { padding: 24px; max-width: 680px; }
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
  .container { padding: 28px; max-width: 740px; }
  /* Add side panels, wider comparisons, etc. */
}
```

**Mobile-specific learning UX rules:**
- Touch targets: minimum 44x44px (Apple HIG), ideally 48x48px
- No hover-dependent interactions — everything must work with tap
- Avoid horizontal scrolling (timelines need a mobile-specific layout)
- Keep quiz options large enough to tap without error
- Compress images and lazy-load media (learners on cellular data)
- Drag-and-drop must have a tap-based alternative on mobile
- Prevent accidental navigation — confirm before leaving a partially-complete lesson
- Use `srcset` / `<picture>` for responsive images
- Target images under 0.5MB for mobile-bandwidth friendliness

**What to progressively enhance on desktop:**
- Side-by-side comparisons (stack vertically on mobile)
- Wider simulator/visualization canvases
- Keyboard shortcuts overlay
- Persistent progress sidebar
- Concept map zoom/pan controls

---

## 6. Animation and Microinteractions

### The Role of Animation in Learning

Animation serves three learning functions:
1. **Directing attention** — Guiding the eye to what changed or matters
2. **Showing process** — Illustrating temporal/causal relationships
3. **Providing feedback** — Confirming actions, celebrating progress

### Evidence-Based Animation Principles

**Quizizz QBit case study (2025):** Their animated mascot's eyes follow the cursor, it hides during password entry, gives motivational nudges — these microinteractions increased engagement without distracting from content.

**Animated tutorials research:** Animations that integrate simulation + embedded assessment + multi-level feedback produce continuous performance data and promote active learning.

**NNGroup's microinteraction model:** Every microinteraction should be a single-purpose trigger → feedback pair: convey system status, prevent errors, reinforce brand personality.

### Animation Taxonomy for Learning

```
Feedback animations (most important):
- ✅ Correct answer: gentle scale-up + color flash (200ms)
- ❌ Wrong answer: subtle shake + muted color (300ms)
- 🎉 Section complete: confetti burst (600ms) — with reduced-motion fallback
- ⬆️ XP gain: counter bump animation (400ms)
- ✨ Achievement unlocked: pop-in with scale overshoot (400ms)

Navigation animations:
- Section reveal: fade-in + translate-up (600ms, staggered)
- Progress bar: smooth width transition (600ms, ease-out)
- Card flip: 3D transform (400ms)
- Accordion expand/collapse: height + opacity (300ms)

Attention-directing animations:
- Pulse on interactive elements waiting for input
- Highlight flash on referenced elements
- Scroll-into-view with gentle ease

Process animations (for teaching):
- Step-by-step build-up of diagrams
- State transitions in simulators
- Data flow visualizations
```

### Performance Rules

- Use CSS transforms and opacity only (GPU-composited, no layout thrash)
- `will-change` on animated elements
- Respect `prefers-reduced-motion: reduce`
- Keep all transitions under 600ms (attention span for UI)
- Use `cubic-bezier(0.4, 0, 0.2, 1)` (Material Design standard ease) for natural feel
- Avoid animating during active reading — animate during transitions between states

---

## 7. What Top Learning Platforms Do Well

### Brilliant.org — "Learn by Doing"

**What they nail:**
- **Problem-first pedagogy**: Every concept is introduced through an interactive problem, never a wall of text. You manipulate, predict, then get the explanation.
- **Game-like simulations**: Learners drag weights, adjust parameters, see consequences. The interaction *is* the learning, not an afterthought.
- **Calibrated difficulty curves**: Problems are carefully sequenced to create flow state — challenging enough to engage, scaffolded enough to not frustrate.
- **Visual-first explanations**: Abstract concepts are made tangible through interactive visualizations before formulas appear.
- **AI-assisted content at scale**: Use AI to generate problem variations while humans design the core learning game mechanics.
- **Spaced and mixed practice**: Reviews surface previously learned material with scaffolding removed to build genuine retrieval.

**Key takeaway**: The unit of learning is the *interactive problem*, not the text paragraph.

### Duolingo — Habit Machine

**What they nail:**
- **Streak mechanics**: RCT evidence (NBER 2025, Peruvian students) shows streak highlighting *causally* increases platform use intensity and improves achievement.
- **Session brevity**: 5-minute lessons create low activation energy for daily practice.
- **Immediate, encouraging feedback**: Every correct answer gets a micro-celebration. Wrong answers get gentle correction with the right answer shown.
- **Visual progress**: The skill tree / path provides a clear map of what's learned and what's ahead.
- **Gamification stack**: XP + streaks + leagues + hearts + achievements — layered mechanics that appeal to different motivation types.
- **Data-driven iteration**: Relentless A/B testing on every UI element and mechanic.

**Key takeaway**: Make the habit easy to start, rewarding to continue, and socially reinforced.

### Khan Academy — Inclusive and Research-Driven

**What they nail:**
- **Accessibility-first rebuilds**: Rewrote graphing with Mafs library for keyboard/screen-reader support.
- **Mastery-based progression**: Clear skill trees with mastery levels (Attempted → Familiar → Proficient → Mastered).
- **Practice + video combination**: Watch explanation, then immediately practice with instant feedback.
- **Clean, distraction-free UI**: Minimal chrome during learning, maximum focus on content.
- **AI integration (Khanmigo)**: But research shows AI/adaptive features need better discoverability.

**Key takeaway**: Accessibility and inclusivity are features, not afterthoughts.

### Execute Program — Unfurling Active Reading

**What they nail:**
- **Text unfurls in response to interaction**: You can't passively scroll. Each prose segment is followed by an interactive prompt. Complete it to reveal the next segment.
- **Write real code, not multiple choice**: Learners type actual expected outputs or code snippets, not pick from options.
- **Spaced repetition built in**: Lessons unlock based on prerequisite mastery; reviews surface previously learned items on a schedule.
- **Short sessions by design**: 5-20 minute cadence, optimized for keyboard-driven flow.
- **No setup friction**: All-in-browser editor/runner, no environment configuration.

**Key takeaway**: Force active recall at every step. Prevent passive consumption structurally.

### 3Blue1Brown / Manim — Visual Mathematical Intuition

**What they nail:**
- **Animation as explanation**: Transforms, morphs, and step-by-step visual builds make abstract math tangible.
- **Programmatic animation**: Manim (Python library) creates reproducible, precise mathematical visualizations.
- **Narration + visual synchronization**: Words and visuals arrive together (Mayer's temporal contiguity principle at d=1.30).
- **Building intuition before formalization**: Show the *why* visually before showing the formula.

**Key takeaway**: Animated, step-by-step visual builds are the most powerful tool for teaching abstract concepts.

### Cross-Platform Design Patterns

| Pattern | Used By | Evidence |
|---|---|---|
| Streak/daily habit mechanics | Duolingo, Brilliant | RCT: increases intensity + achievement |
| Interactive before explanation | Brilliant, Execute Program | Active learning > passive reading |
| Progress visualization (path/tree) | Duolingo, Khan Academy | Motivates continuation, shows mastery |
| Spaced repetition/review | Execute Program, Duolingo | Retrieval practice strengthens memory |
| Immediate specific feedback | All of the above | Formative assessment literature |
| Short session design (5-20 min) | All of the above | Reduces activation energy |
| Accessible-first interactive content | Khan Academy | Inclusive design is better design |
| Animations synchronized with content | 3Blue1Brown | Temporal contiguity effect (d=1.30) |

---

## 8. Interactive Visualizations for Learning

### Library Selection Guide

| Library | Best For | Complexity | Learning Use Case |
|---|---|---|---|
| **D3.js** | Data visualization, interactive charts, graphs | High | Statistics, data science, network diagrams |
| **p5.js** | Creative coding, physics sims, visual math | Medium | Art, physics, geometry, algorithms |
| **Three.js** | 3D visualizations, spatial concepts | High | Chemistry (molecules), architecture, 3D math |
| **Manim** | Programmatic math animation | Medium | Calculus, linear algebra, proofs |
| **Mermaid.js** | Diagrams, flowcharts, concept maps | Low | Architecture, processes, relationships |
| **Observable Plot** | Quick data charts, statistical graphics | Low | Data literacy, statistics |
| **Mafs** | Accessible math coordinate graphics | Low | Algebra, functions, geometry (a11y-first) |
| **Canvas API** | Custom low-level drawing, games | Medium | Custom simulations, educational games |

### The Explorable Explanations Ecosystem

[explorabl.es](https://explorabl.es/) is the community hub for interactive educational content. Key patterns from the best examples:

1. **Reactive sliders/inputs** that immediately update a visualization (Bret Victor's "Tangle" model)
2. **Linked representations** — manipulate a graph and see the equation update, or vice versa
3. **Stepper controls** — step through a process frame-by-frame with play/pause
4. **Sandboxed simulations** — learner adjusts initial conditions, hits "run," observes outcomes
5. **Annotated animations** — labels and callouts that appear synchronized with animation steps

### Implementation Recommendations

For the interactive-learner skill specifically:

- **Concept maps**: Already using Mermaid.js — excellent choice for low complexity
- **Simulators**: The current `simulator` component with raw JS handlers is flexible but fragile. Consider standardized simulation patterns (state machine + render function + event handlers)
- **Math content**: Consider Mafs (React) or KaTeX rendering + interactive parameter widgets
- **Data visualizations**: Observable Plot for quick charts; D3 for complex interactive graphics
- **Creative/physics sims**: p5.js sketches embedded via `<script>` — perfect for the `custom` component type

---

## 9. The Role of Immediate Feedback

### Why Speed Matters

- **< 100ms**: Perceived as instant. Ideal for button press acknowledgment.
- **100-200ms**: Feels responsive. Target for quiz answer feedback.
- **200-1000ms**: Noticeable delay. Acceptable for complex computations.
- **> 1000ms**: Feels slow. Needs a loading indicator.

For learning: answer feedback should appear within 200ms. The delay between action and consequence is the delay in forming the association.

### Feedback Design Principles

**Multi-level feedback** (from Lambda Feedback, EDUCON 2025):
1. **Level 1 — Binary**: Correct/incorrect (immediate visual)
2. **Level 2 — Explanatory**: Why it's right/wrong (appears after Level 1)
3. **Level 3 — Instructional**: What to study/try next (appears if wrong)
4. **Level 4 — Metacognitive**: "You tend to confuse X with Y" (aggregated over time)

**Feedback that teaches, not just judges:**
```
❌ Bad:  "Incorrect. Try again."
❌ Okay: "Incorrect. The answer is B."
✅ Good: "Not quite — Pods wrap containers, they don't replace them.
          A Pod can hold multiple containers that share networking."
✅ Best: "Not quite — you chose 'replaces containers' but Pods actually
          *wrap* containers. Think of a Pod as an envelope: it doesn't
          replace the letter inside, it groups and addresses it."
```

**Positive feedback should also teach:**
```
❌ Bad:  "Correct!"
✅ Good: "Exactly — Pods wrap containers so Kubernetes can manage them
          as a single schedulable unit. This is why a Pod can have
          sidecar containers."
```

### System Design for Real-Time Feedback

- **Client-side validation** for deterministic answers (MCQ, matching, ordering, fill-blank). No server round-trip needed.
- **Microservice architecture** for complex evaluation (code execution, math symbolic checking). Lambda Feedback processes ~1M events/year with teacher-configurable feedback.
- **Streaming feedback** for AI-generated responses — show feedback character-by-character for natural feel.
- **Confusion detection** — micro-contest/polling mechanisms (Challengr) surface common misconceptions in real-time for instructor intervention.

---

## 10. Progressive Disclosure and Cognitive Load Management

### Progressive Disclosure in Learning Interfaces

**Core principle**: Show only what's needed right now. Defer complexity to when the learner is ready.

**Layered interface evidence (Open University, 2025)**: Interfaces that progressively reveal features based on user skill measurably improve learnability and reduce training time.

### Techniques for Learning UIs

**Content-level progressive disclosure:**
- Click-to-reveal explanations (details/summary)
- Tabbed content panels (overview / details / examples)
- Expandable "Learn More" sections after core content
- Collapsible code blocks (show output first, reveal code on demand)
- Hint systems: Hint 1 → Hint 2 → Show Answer (escalating support)

**Interface-level progressive disclosure:**
- Start with core actions only; surface advanced features after mastery
- Show simple exercise variants first; unlock complex variants after success
- Navigation: show only current section + breadcrumb, not entire lesson outline
- Settings/customization: sensible defaults first, power-user options discoverable

**Session-level progressive disclosure (Execute Program model):**
- Text appears in small chunks
- Each chunk ends with an interactive prompt
- Completing the prompt reveals the next chunk
- Cannot skip ahead — ensures active processing of each segment

### Cognitive Load Reduction Strategies

| Strategy | Implementation | Mayer Principle |
|---|---|---|
| Chunking | Break lessons into 5-7 concept groups | Segmenting |
| Pre-training | Teach key vocabulary before the main lesson | Pre-training |
| Signaling | Bold key terms, color-code categories, use icons | Signaling |
| Weeding | Remove decorative images, tangential examples | Coherence |
| Spatial grouping | Place labels ON or directly adjacent to diagrams | Spatial Contiguity |
| Temporal sync | Show text and visual simultaneously | Temporal Contiguity |
| Worked examples | Show complete solved examples before practice | Worked Example Effect |
| Fading | Gradually remove scaffolding as learner progresses | Expertise Reversal |

### Anti-Patterns (What Increases Cognitive Load)

- Showing all quiz questions at once instead of one-at-a-time
- Walls of text before any interaction
- Multiple competing animations on screen simultaneously
- Navigation that requires understanding the full course structure
- Dense sidebars with links, stats, and options during active learning
- Auto-playing video or audio alongside text content
- Requiring learners to context-switch between tools/windows

---

## 11. Dark Mode, Customization, and Learner Preferences

### Dark Mode Research (2025)

**Key finding**: Preferences vary by age, device, ambient lighting, and task type. There is no universally "better" mode. Offering choice is the only correct approach.

**Evidence-based dark mode design:**

```css
/* Good dark mode (current shell.html approach) */
--bg: #111114;          /* Dark gray, NOT pure black */
--card: #1a1a20;        /* Raised surface, subtle differentiation */
--text: #d8d8e0;        /* Off-white, NOT pure white */
--text-mid: #9898ac;    /* Secondary text, sufficient contrast */

/* Light mode equivalent */
--bg: #f8f8fa;
--card: #ffffff;
--text: #1a1a2e;
--text-mid: #64648a;
```

**Dark mode rules:**
1. Use dark grays (#111-#1a1a), not pure black (#000)
2. Use off-white (#d8d8-#e8e8), not pure white (#fff) for body text
3. Maintain 4.5:1+ contrast ratios in both modes
4. Check focus state visibility in dark mode (often breaks)
5. Reduce image brightness/saturation slightly in dark mode
6. Shadows don't work in dark mode — use borders or subtle glows instead
7. Test both modes with actual content, not just components

### Learner Preference Controls

**Minimum viable customization:**
- Light/dark/system mode toggle
- Font size adjustment (3 steps: normal, large, extra-large)
- Reduced motion toggle

**Enhanced customization:**
- Line height adjustment
- Letter spacing adjustment
- Content width (narrow/medium/wide)
- High contrast mode
- Dyslexia-friendly font option (OpenDyslexic or similar)
- Reading ruler/guide overlay

**Implementation pattern:**
```javascript
// Store preferences in localStorage
const prefs = {
  theme: 'system', // 'light' | 'dark' | 'system'
  fontSize: 'normal', // 'normal' | 'large' | 'xlarge'
  reducedMotion: false,
  lineHeight: 'normal', // 'normal' | 'relaxed' | 'spacious'
};

// Apply via CSS custom properties on <html>
document.documentElement.dataset.theme = resolved;
document.documentElement.style.setProperty('--font-scale', scale);
```

**Persist across sessions.** Nothing is more frustrating than re-configuring preferences every time you open a lesson.

---

## 12. Embeddable Learning Components

### Platform Comparison

| Platform | Embed Method | Best For | Interactivity | Offline |
|---|---|---|---|---|
| **Observable** | iframe, JS runtime, ES modules | Data viz, reactive notebooks | Full (cells run live) | ES module export |
| **CodePen** | iframe embed | HTML/CSS/JS demos | Full | No |
| **Sandpack** | React component | Live code editor+preview | Full (hot reload, npm) | Bundle locally |
| **CodeSandbox** | iframe embed | Full project sandboxes | Full | No |
| **JupyterLite** | iframe embed | Python REPL, data science | Full (Pyodide/WASM) | Yes (WASM) |
| **Manim** | Pre-rendered video/GIF | Math animation | Passive (pre-rendered) | Yes |
| **p5.js** | Inline `<script>` or iframe | Creative coding, simulations | Full | Yes |
| **Mermaid.js** | Inline `<script>` rendering | Diagrams, flowcharts | Limited (static render) | Yes |

### For the Interactive-Learner Skill Specifically

The current architecture (JSON → build-lesson.py → static HTML) has a huge advantage: **everything works offline, on `file://`**. This is rare and valuable. Prioritize embed approaches that preserve this:

**Tier 1 — Inline (preserves file:// and offline):**
- Mermaid.js diagrams (already used in concept-map component)
- p5.js sketches via `<script>` tag with CDN fallback
- KaTeX math rendering (inline)
- Custom Canvas API interactions
- Vanilla JS simulators (already in simulator component)

**Tier 2 — CDN-dependent (works offline with service worker, but needs initial load):**
- D3.js visualizations
- Three.js 3D scenes
- Prism.js / highlight.js code highlighting
- Chart.js / Observable Plot

**Tier 3 — Requires online + iframe:**
- Sandpack live code editors
- JupyterLite REPLs
- CodePen/CodeSandbox embeds
- Observable notebook embeds

**Recommendation**: Stay in Tier 1-2 for core lesson content. Use Tier 3 only for optional "deep dive" exercises that link out or embed via iframe with graceful degradation.

### Web Components as Learning Primitives

The standards-based Web Components API (Custom Elements + Shadow DOM + Templates/Slots) offers a path to creating reusable, encapsulated learning widgets:

```html
<!-- Potential future: custom elements for each component type -->
<learn-quiz questions='[...]'></learn-quiz>
<learn-vocab terms='[...]'></learn-vocab>
<learn-simulator config='...'></learn-simulator>
```

Benefits:
- Framework-agnostic (works in any HTML page)
- Encapsulated styles (Shadow DOM prevents conflicts)
- Composable and reusable
- Progressive enhancement friendly

This is a future architectural direction, not a current priority — the JSON → Python → HTML pipeline is simpler and working well.

---

## Synthesis: Actionable Design Principles

### The 10 Commandments of Learning Frontend Design

1. **Active before passive.** Every screen should require the learner to *do* something before they can advance. Text unfurls in response to interaction, not scrolling.

2. **One concept per viewport.** Each screen-height section has one focus. No competing elements. Generous whitespace.

3. **Feedback in 200ms.** Correct/incorrect visual feedback appears instantly. Explanatory feedback follows within 500ms. Never make a learner wonder "did that work?"

4. **Progressive disclosure everything.** Show the minimum needed. Reveal complexity as competence grows. Hints escalate. Features unlock.

5. **Mobile-first, keyboard-accessible.** Design for thumb on phone, test with keyboard on desktop. Touch targets 48px. Every interactive element reachable via Tab.

6. **Animate with purpose.** Every animation directs attention, shows process, or provides feedback. No decorative animation. Respect `prefers-reduced-motion`.

7. **Chunk ruthlessly.** 5-7 concepts per lesson. 1-3 sentences per chunk. 3-4 vocab terms max per session. Break complex ideas into steps.

8. **Personalize the path.** Adapt difficulty, surface reviews, track mastery. But make adaptive features visible and integrated — not hidden.

9. **Beautiful ≠ busy.** The best learning interfaces feel calm and spacious. Dark backgrounds, high-contrast text, generous padding, minimal borders.

10. **Accessibility is the floor.** WCAG AA minimum. Keyboard navigation. Screen reader support. Color is never the only indicator. This isn't optional — it makes the product better for everyone.

### Priority Implementation Roadmap

**Phase 1 — Foundation (current state → polished)**
- [ ] Add light mode + system preference detection
- [ ] Add font size controls (3 steps)
- [ ] Add `prefers-reduced-motion` support
- [ ] Ensure all components are keyboard-navigable
- [ ] Add ARIA labels and live regions to interactive components
- [ ] Validate touch target sizes for mobile
- [ ] Add responsive breakpoints to shell.html

**Phase 2 — Enhanced Interactions**
- [ ] Implement hint escalation system (Hint 1 → Hint 2 → Answer)
- [ ] Add multi-level feedback to quiz component (why right + why wrong)
- [ ] Create "unfurling" mode where sections reveal after interaction
- [ ] Add spaced repetition / review session generation
- [ ] Build code-execution component (for programming topics)

**Phase 3 — Advanced Features**
- [ ] Streak tracking + daily habit mechanics
- [ ] Achievement system with meaningful milestones
- [ ] Embeddable p5.js sketches for visual simulations
- [ ] D3.js visualization component type
- [ ] Difficulty adaptation based on quiz performance
- [ ] Learner preference persistence across sessions

---

## Sources

### Academic & Research
- Mayer, R.E. — Cognitive Theory of Multimedia Learning (effect sizes: multimedia d=1.67, temporal contiguity d=1.30)
- Sweller, J. — Cognitive Load Theory (extraneous/intrinsic/germane framework)
- PACIS 2025 — "How Do Interactive Features Improve Digital Learning Performance" (guidance vs. exploration trade-off)
- Frontiers in Computer Science 2025 — AI-powered adaptive learning interfaces (Khan/Coursera/Codecademy study)
- Open University 2025 — "Designing for Learnability: Improvement Through Layered Interfaces"
- NBER 2025 — "Streaks to Success" (RCT on streak mechanics and student achievement)
- Lambda Feedback, EDUCON 2025 — Real-time formative feedback at scale
- Readability Consortium — Typography personalization study (n=94, K-8)
- TechRxiv 2025 — Effects of dark mode on university students

### Platform Analysis
- Brilliant.org — blog.brilliant.org/hand-crafted-machine-made (AI + content design)
- Duolingo — everydayux.net handbook analysis (9 design lessons)
- Khan Academy — blog.khanacademy.org (accessibility graph rebuild with Mafs)
- Execute Program — executeprogram.com/why-ep + Andy Matuschak's analysis

### Design Resources
- Bret Victor — worrydream.com/ExplorableExplanations (reactive documents)
- Nicky Case — blog.ncase.me (Do/Show/Tell, Interest Curves, Ladder of Abstraction)
- explorabl.es — community hub for interactive educational content
- NNGroup — nngroup.com/articles/microinteractions
- Interaction Design Foundation — Progressive Disclosure topic

### Technical
- Observable — observablehq.com/documentation/embeds (embedding guide)
- Sandpack — sandpack.codesandbox.io (live code editor toolkit)
- JupyterLite — jupyterlite.readthedocs.io (embeddable Python REPL)
- Manim Community — manim.community (math animation library)
- W3C — WCAG 3.0 Working Draft (Sept 2025), ATAG for LMS
- UK DfE — Accessibility and Inclusive Design Manual
