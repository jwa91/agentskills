# Embeddable React/TypeScript Components for the Interactive Learner Skill

## Research Analysis — Feasibility, Approaches, and Recommendations

---

## 1. Current Architecture

The Interactive Learner skill currently:

- Generates **lesson JSON** (~60-100 lines) describing sections with typed components
- Runs a **Python build script** (`build-lesson.py`) that transforms JSON → standalone HTML
- Uses an **HTML shell template** (`shell.html`) with embedded CSS/JS — dark theme, animations, progress tracking
- Each component renderer (Python function) emits `(html_str, js_str)` tuples
- Output is a single `.html` file opened in the browser — **fully self-contained, zero dependencies**

This is elegant in its simplicity: the agent writes JSON, runs one command, and the student gets a complete interactive lesson. No build toolchain, no npm, no bundler, no framework runtime needed on the student's machine.

---

## 2. Approaches Evaluated

### 2A. Web Components (Custom Elements) — Framework-Agnostic Embedding

**How it works:** Define `<lesson-quiz>`, `<lesson-vocab-cards>`, `<lesson-timeline>` etc. as Custom Elements. Each uses Shadow DOM for style isolation. Consumers embed via `<script src="learner-components.js">` + custom element tags.

**Tooling options:**

- **Stencil.js** — Compile-time tool producing standards-compliant Web Components from TypeScript + JSX. Tiny runtime, lazy-loading, multiple output targets (dist, dist-custom-elements). Used by Ionic.
- **Lit** — Google's lightweight library for Web Components. Reactive properties, declarative templates, ~5KB runtime.
- **@r2wc/react-to-web-component** — Wraps existing React components as Custom Elements. Allows writing in React but distributing as native elements.
- **Vanilla** — No framework, just `class extends HTMLElement` with Shadow DOM.

**Pros:**

- Framework-agnostic: works in React, Vue, Angular, plain HTML, WordPress, anywhere
- Shadow DOM provides true style isolation (no CSS leakage to/from host)
- Native browser standard — no framework lock-in
- Can be distributed as a single JS file via CDN
- Progressive enhancement: `<lesson-quiz data-config='...'>` degrades to invisible if JS fails

**Cons:**

- Shadow DOM complicates theming (only CSS custom properties and `::part()` cross the boundary)
- Inherited CSS properties still leak in (font-family, color, line-height)
- Declarative Shadow DOM for SSR has varying browser support
- Learning curve for Stencil/Lit if the skill currently outputs vanilla HTML
- Agent would need to generate either JSON config (current approach) or Web Component markup

**Verdict:** Strong option for **distribution** of a component library, but overkill for what an agent skill does per-session. Better suited as a long-term packaging target.

---

### 2B. Embeddable React/TypeScript Components (Bundled Widget)

**How it works:** Author components in React + TypeScript, bundle with esbuild/Rollup/Vite into a single JS file. Consumers either `npm install` or include a `<script>` tag and call an init function.

**Tooling chain:**

```
Agent writes JSON → build script generates .tsx files → esbuild bundles → single .js widget
```

Or more practically:

```
Agent writes JSON → build script generates HTML that includes pre-built React component library
```

**Pros:**

- Rich component authoring with React's ecosystem (hooks, state, animations)
- TypeScript gives compile-time safety for component props
- Can produce both ESM (modern) and UMD/IIFE (legacy) bundles
- esbuild is extremely fast (~10ms to bundle a widget)
- Components can be tree-shaken — only include what the lesson uses

**Cons:**

- Requires React runtime (~40KB minified+gzipped for React 18) — significant overhead for a learning widget
- Dependency conflicts if host page also uses React (version mismatches)
- More complex build pipeline than current Python→HTML approach
- Agent would need Node.js / esbuild available (or use esbuild-wasm in-browser)

**Verdict:** Good if the target consumer is a React app. Bad if the goal is "drop into any website." The React dependency tax is real.

---

### 2C. Module Federation (Webpack 5 / Vite)

**How it works:** Remote applications expose modules that host applications load at runtime. A "learning widget" remote could expose `<QuizComponent>`, `<VocabCards>`, etc. Hosts dynamically import them.

**Relevant tooling:**

- Webpack 5 `ModuleFederationPlugin`
- `@module-federation/vite` plugin
- Module Federation v2 with Rspack support

**Pros:**

- Runtime loading — no rebuild of host app needed
- Shared dependencies (React, etc.) negotiated at runtime — avoids duplication
- True micro-frontend architecture

**Cons:**

- **Requires both host AND remote to use Module Federation** — consumers need specific Webpack/Vite config
- Extremely heavy infrastructure for what is essentially a learning widget
- Not a "drop a script tag" solution
- Version negotiation can fail at runtime causing hard-to-debug errors
- Assumes a persistent deployment server for the remote (CDN or service)

**Verdict:** Wrong tool for this job. Module Federation is designed for large organizations splitting monolithic SPAs, not for distributing embeddable educational widgets.

---

### 2D. iframe-Based Embedding (Current Approach Extended)

**How it works:** Serve the current standalone HTML files from a URL. Consumers embed via `<iframe src="https://lessons.example.com/lesson-42.html">`.

**Pros:**

- **Strongest isolation** — separate browsing context, completely independent DOM/CSS/JS
- Zero risk of style/script conflicts with host page
- Current HTML files already work perfectly as iframe content
- Simple for consumers: one `<iframe>` tag
- Can sandbox with `sandbox` attribute for security
- Resize with `postMessage` communication

**Cons:**

- Performance overhead of separate browsing context
- No shared styling with host page (can't inherit theme)
- Cross-origin communication requires `postMessage` — clunky for events/data
- Mobile responsiveness inside iframes is tricky (viewport within viewport)
- SEO-invisible content
- Feels "embedded" rather than "native" — visible iframe boundaries, scroll-within-scroll

**Verdict:** The **easiest path** from the current system. Already works. Good for LMS integration (this is exactly what H5P does). But limited integration depth.

---

### 2E. Hybrid: Self-Contained HTML + Optional Web Component Wrapper

**How it works:** Keep the current build pipeline (JSON → HTML) but also generate a thin Web Component wrapper that can load the lesson content.

```html
<!-- Current standalone usage — unchanged -->
<open lesson.html in browser>
  <!-- New: embed in any page -->
  <script src="interactive-lesson.js"></script>
  <interactive-lesson src="lesson.json"></interactive-lesson>

  <!-- New: embed in any page via iframe (zero-change) -->
  <iframe src="lesson.html" width="100%" height="800"></iframe
></open>
```

The Web Component wrapper would:

1. Create a Shadow DOM root
2. Inject the shell HTML + CSS into the shadow root
3. Load the lesson JSON and render sections
4. Expose attributes/properties for theming overrides

**Pros:**

- Backward-compatible — standalone HTML still works exactly as today
- Web Component version gives native embedding with style isolation
- iframe version requires zero changes
- Incremental: build the Web Component wrapper as a separate deliverable
- No React dependency — pure vanilla JS + Shadow DOM
- Can still be generated entirely by a Python build script

**Cons:**

- Need to refactor current per-component CSS/JS to work inside Shadow DOM
- Two rendering paths to maintain (standalone + shadow DOM)
- Agent still primarily generates JSON; the Web Component is a distribution concern

---

### 2F. In-Browser TypeScript Compilation (esbuild-wasm)

**How it works:** Use esbuild-wasm to compile TypeScript/TSX in the browser without Node.js. The agent generates .tsx source, and it's compiled client-side.

**Pros:**

- No Node.js or build toolchain needed on the user's machine
- Could enable "live editing" of lesson components
- esbuild-wasm is fast even in-browser

**Cons:**

- ~8MB wasm binary to download
- Still needs React runtime loaded separately
- Compilation errors surface at runtime, not build time
- Significant complexity for marginal benefit over pre-built HTML
- Not actually simpler than the current Python build approach

**Verdict:** Interesting for an interactive playground/editor feature, but not a practical replacement for the current build pipeline.

---

## 3. Precedent: How Learning Platforms Handle This

### H5P (Most Relevant Precedent)

H5P is the closest existing analogy to what this skill does:

| Aspect           | H5P                                      | Interactive Learner Skill           |
| ---------------- | ---------------------------------------- | ----------------------------------- |
| Content format   | JSON (`content.json`) + metadata         | JSON (lesson config)                |
| Component system | "Libraries" with `library.json` + JS/CSS | Python renderers outputting HTML/JS |
| Packaging        | `.h5p` ZIP files                         | Single `.html` file                 |
| Embedding        | iframe or LTI integration                | Open in browser                     |
| Style isolation  | Per-library CSS scoping                  | Single-file, no isolation needed    |
| Editor           | Visual editor with semantic schemas      | AI agent generates JSON             |
| Distribution     | H5P Hub, LMS plugins, LTI                | Local filesystem                    |

**Key insight from H5P:** They separate **content** (JSON) from **rendering** (libraries/runtime) and from **hosting** (plugins/LTI). This three-layer separation is what enables embeddability. The Interactive Learner skill already has the first two layers — it just lacks the hosting/embedding layer.

### Khan Academy

- Custom React component library, not embeddable outside their platform
- Content is deeply coupled to their infrastructure (video player, exercise framework, mastery system)

### Coursera / edX

- Use LTI (Learning Tools Interoperability) for third-party content embedding
- XBlocks (edX) are Python-rendered HTML components — very similar to our architecture

### Observable

- Exports ES modules that return DOM elements
- Framework-agnostic: any page can `import` and mount them
- Excellent model for data-driven interactive components

---

## 4. Can an Agent Skill Realistically Generate and Serve TypeScript Components?

### What exists today (2025-2026)

Several projects prove this is feasible:

- **Hashbrown** — Framework for LLMs to compose real React views at runtime, streaming component props
- **ReactAgent** — Autonomous agent generating TypeScript React components from user stories
- **Codebolt** — SDK with a "React Component Generator Agent" producing .tsx files + tests + Storybook stories
- **Lovable** — Chat agent doing multi-file TypeScript+React generation with one-click deployment

### But the practical question is different

The question isn't "can an AI generate TypeScript components?" (yes, trivially). It's: **"does generating TypeScript components improve the learning experience over generating JSON that builds to HTML?"**

**Arguments FOR generating React/TS components:**

- Richer interactivity (complex state machines, animations, async data)
- Components could be shared/reused across lessons
- TypeScript catches structural errors at compile time
- Opens the door to a component marketplace

**Arguments AGAINST:**

- Adds a **mandatory build step** that requires Node.js
- Current JSON → HTML pipeline is ~10 lines of JSON for a full interactive lesson
- The agent already has full creative freedom via the `"type": "custom"` component
- Students don't need (or want) a toolchain — they need a lesson
- TypeScript compilation errors from AI-generated code would be a terrible UX
- The current approach already achieves **100% of the interactive functionality** needed

---

## 5. Trade-off Matrix

| Criterion                     | Standalone HTML (current) | Web Components | React Bundle | Module Federation | iframe Embed | Hybrid (HTML + WC) |
| ----------------------------- | :-----------------------: | :------------: | :----------: | :---------------: | :----------: | :----------------: |
| **Works anywhere**            |          **A+**           |       A        |      B       |         D         |      A       |       **A+**       |
| **Zero dependencies**         |          **A+**           |       A        |      C       |         D         |    **A+**    |         A          |
| **Style isolation**           |            N/A            |       A        |      B       |         B         |    **A+**    |         A          |
| **Build complexity**          |   **A+** (Python only)    |       B        |      C       |         D         |    **A+**    |         B          |
| **Agent generation ease**     |       **A+** (JSON)       |       B        |      C       |         C         |    **A+**    |         A          |
| **Embeddable in other sites** |             D             |     **A+**     |      B       |         C         |      A       |       **A+**       |
| **Host page integration**     |             D             |       A        |    **A+**    |         A         |      D       |         A          |
| **Performance**               |          **A+**           |       A        |      B       |         B         |      C       |         A          |
| **Interactive richness**      |             A             |       A        |    **A+**    |         A         |      A       |         A          |
| **Incremental from current**  |          **A+**           |       C        |      D       |         D         |      A       |       **A**        |

---

## 6. Recommendation

### Short-term: Enhance the current approach (no architecture change)

The current JSON → standalone HTML pipeline is already excellent for its purpose. The agent generates concise JSON, the build script produces a polished interactive lesson. **There is no gap in interactive capability** — the `custom` component type already allows arbitrary HTML/CSS/JS.

**Immediate improvements that don't require new architecture:**

1. Add a `--embed` flag to `build-lesson.py` that outputs a version optimized for iframe embedding (no `<html>`/`<head>`, just the content div + scoped styles)
2. Add `postMessage`-based score reporting so iframe-embedded lessons can report completion back to the host page
3. Generate a `<meta>` tag with CORS headers for cross-origin iframe embedding

### Medium-term: Web Component wrapper (parallel deliverable)

Build a **single JavaScript file** (`interactive-lesson.js`, ~50-80KB) that:

1. Registers `<interactive-lesson>` as a Custom Element
2. Accepts a `config` attribute/property (the lesson JSON) or a `src` attribute (URL to lesson JSON)
3. Creates a Shadow DOM root with the shell CSS
4. Renders lesson sections using the same component logic, but in JS instead of Python
5. Exposes CSS custom properties for host-page theming (colors, fonts)
6. Emits Custom Events for progress/completion/score

This would be a **JavaScript port of `build-lesson.py`'s rendering logic** — not a React app, not TypeScript, just clean vanilla JS with Shadow DOM. It could be:

- Served from a CDN
- Included via `<script>` tag
- Used in any framework (React, Vue, Angular, vanilla)
- Generated by the agent skill alongside the current HTML output

The agent's workflow wouldn't change — it still generates lesson JSON. But consumers gain a new embedding option.

### Long-term: Consider React/TypeScript only if...

Moving to React/TypeScript component generation would only be justified if:

1. **The skill needs to integrate into existing React applications** as first-class components (not widgets)
2. **Complex state management** emerges that vanilla JS can't handle cleanly (unlikely for learning content)
3. **A component marketplace** develops where lesson authors share and remix interactive components
4. **The toolchain burden is eliminated** — e.g., the agent can deploy to a CDN with zero user setup

Even then, the recommended approach would be:

- Author components in React/TypeScript
- Compile them to Web Components via Stencil or `@r2wc/react-to-web-component`
- Distribute the compiled output — consumers never need React

### What NOT to do

- **Don't use Module Federation.** It solves a completely different problem (splitting large SPAs) and requires consumers to adopt specific build tooling.
- **Don't require Node.js on the student's machine.** The current zero-dependency approach is a feature, not a limitation.
- **Don't generate TypeScript files that need compilation.** The agent should produce ready-to-use output, not source code that requires a build step.
- **Don't use in-browser esbuild-wasm.** It's a solution looking for a problem in this context.

---

## 7. Proposed Architecture (Medium-Term)

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT GENERATES                          │
│                                                             │
│                      lesson.json                            │
│                 (same format as today)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
         ┌──────────────────┼────────────────────┐
         ▼                  ▼                    ▼
  ┌──────────────┐   ┌────────────┐  ┌──────────────────────┐
  │ build-lesson │   │ Web Comp   │  │  iframe embed        │
  │ .py          │   │ runtime    │  │  (no change needed)  │
  │              │   │            │  │                      │
  │ JSON → HTML  │   │ JSON → DOM │  │  serve .html file    │
  │ (standalone) │   │ (Shadow    │  │  in <iframe>         │
  │              │   │  DOM)      │  │                      │
  └──────┬───────┘   └─────┬──────┘  └───────────┬──────────┘
         ▼                 ▼                     ▼
  ┌─────────────┐  ┌────────────────┐  ┌──────────────────┐
  │ lesson.html │  │ <interactive-  │  │ <iframe src=     │
  │ (open in    │  │  lesson        │  │  "lesson.html">  │
  │  browser)   │  │  config='...'> │  │                  │
  └─────────────┘  └────────────────┘  └──────────────────┘
     Student         Any website         Any website
     (direct)        (native embed)      (isolated embed)
```

### Key: the lesson JSON is the single source of truth

All three output paths consume the same JSON. The agent's job doesn't change. The Python build script remains the primary path. The Web Component runtime is a bonus distribution channel built once and maintained as a library.

---

## 8. Implementation Sketch for Web Component Wrapper

If you decide to proceed with the Web Component approach, here's a minimal starter:

```javascript
// interactive-lesson.js — registers <interactive-lesson> custom element

class InteractiveLesson extends HTMLElement {
  static get observedAttributes() {
    return ["src", "config"];
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  async connectedCallback() {
    const config = this.getAttribute("config")
      ? JSON.parse(this.getAttribute("config"))
      : await fetch(this.getAttribute("src")).then((r) => r.json());

    this.render(config);
  }

  render(config) {
    this.shadowRoot.innerHTML = `
      <style>${SHELL_CSS}</style>
      <div class="container">
        ${config.sections.map((s, i) => renderSection(s, i)).join("")}
      </div>
    `;
    // Initialize interactive JS for quizzes, matching, etc.
    this.initInteractions();
  }

  initInteractions() {
    // Port of the JS logic currently embedded in build-lesson.py output
  }
}

customElements.define("interactive-lesson", InteractiveLesson);
```

Consumer usage:

```html
<!-- Option A: inline config -->
<script src="https://cdn.example.com/interactive-lesson.js"></script>
<interactive-lesson config='{"title":"...","sections":[...]}'></interactive-lesson>

<!-- Option B: external JSON -->
<interactive-lesson src="/lessons/kubernetes-101.json"></interactive-lesson>
```

---

## 9. Summary

| Question                                                    | Answer                                                                                     |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Should the skill generate TypeScript/React instead of HTML? | **No.** HTML generation is simpler, faster, and already fully capable.                     |
| Should the skill support embeddable output?                 | **Yes.** iframe embedding works today; Web Components would add native embedding.          |
| Best embedding approach?                                    | **Hybrid: keep HTML + add Web Component wrapper.**                                         |
| Is Module Federation relevant?                              | **No.** Wrong scale and wrong consumer model.                                              |
| Is Shadow DOM useful?                                       | **Yes.** Essential for the Web Component wrapper's style isolation.                        |
| Can an agent generate TS components?                        | **Yes, but it shouldn't.** JSON → pre-built renderer is better than TS → compile → render. |
| Best precedent to follow?                                   | **H5P** (JSON content + JS runtime + multiple embed targets).                              |
| Biggest risk of changing approaches?                        | Losing the zero-dependency simplicity that makes the current skill reliable.               |
