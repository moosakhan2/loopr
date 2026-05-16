# Architecture Diagrams — Recursive Testing Agent

This file contains the architectural views for the project. All diagrams use [Mermaid](https://mermaid.js.org/), which renders natively on GitHub, GitLab, VS Code (with the Markdown Preview Mermaid Support extension), and Obsidian.

Keep this file at the repo root as `ARCHITECTURE.md` so AI editors and teammates can reference it.

---

## 1. High-level architecture

The full system at a glance: who calls what, where intelligence comes from, and where memory lives.

```mermaid
flowchart TB
    User([Developer])

    subgraph Interface
        CLI[CLI<br/><i>cli.py</i>]
    end

    subgraph Orchestration
        Loop[Loop controller<br/><i>loop.py</i>]
    end

    subgraph Intelligence
        Gen[Test generator<br/><i>generator.py</i>]
        Fix[Fix suggester<br/><i>fixer.py</i>]
        WX[watsonx.ai client<br/><i>watsonx_client.py</i>]
    end

    subgraph Execution
        Runner[Test runner<br/><i>runner.py</i>]
        Sample[(Sample repo<br/>under test)]
    end

    subgraph Memory
        Bank[Context bank<br/><i>context_bank.py</i>]
        JSON[(.agent-context.json)]
    end

    User -->|run command| CLI
    CLI --> Loop
    Loop --> Gen
    Loop --> Runner
    Loop --> Fix
    Loop <-->|read / write| Bank
    Gen --> WX
    Fix --> WX
    WX -->|API call| Watsonx[(IBM watsonx.ai)]
    Runner --> Sample
    Bank --> JSON
```

**Key idea:** `Loop controller` is the only module that orchestrates. Every other module is a pure function that takes input and returns output. The `Context bank` is read **before** each step and written **after** each iteration.

---

## 2. Recursive loop sequence

What happens during a single run of the CLI, step by step.

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant C as CLI
    participant L as Loop
    participant B as Context bank
    participant G as Generator
    participant W as watsonx.ai
    participant R as Runner
    participant F as Fixer

    U->>C: python -m agent.cli ./sample-repo
    C->>L: run(path)
    L->>B: load()
    B-->>L: context (history, requirements)

    loop until all_passing or max iterations
        L->>G: generate_tests(code, context)
        G->>W: prompt with history
        W-->>G: test functions
        G-->>L: list of tests
        L->>R: run_tests(tests, path)
        R-->>L: results
        alt all tests pass
            L->>L: exit loop
        else some tests fail
            L->>F: suggest_fix(failures, code, context)
            F->>W: prompt with failures + history
            W-->>F: patch + explanation
            F-->>L: fix proposal
            L->>B: append_history(bug, fix)
        end
    end

    L-->>C: summary
    C-->>U: print results
```

**Key idea:** the loop is the *recursive* part. Each iteration's bugs and fixes are appended to the context bank, so the next iteration's prompts include that history.

---

## 3. The differentiator — what makes run 2 different from run 1

This is the diagram to point at during the demo. It shows why the persistent context bank matters.

```mermaid
flowchart LR
    subgraph Run1[Run 1 — cold start]
        R1[Empty context] --> G1[Generator] --> T1[Generic tests]
        T1 --> Bugs1[Finds bugs A, B, C]
        Bugs1 --> Save1[Save to context]
    end

    subgraph Run2[Run 2 — warm start]
        Save1 -.persists.-> R2[Context with<br/>bugs A, B, C]
        R2 --> G2[Generator] --> T2[Targeted tests<br/>avoiding past mistakes]
        T2 --> Bugs2[Finds deeper bugs D, E]
    end

    style R1 fill:#fbeaf0,stroke:#993556
    style R2 fill:#eaf3de,stroke:#3b6d11
    style Save1 fill:#e6f1fb,stroke:#185fa5
```

**Key idea:** without the context bank, run 2 would repeat run 1. The persistence is what turns this from a test generator into an agent that learns your codebase.

---

## 4. Module ownership

Who owns what during the hackathon. Useful for stand-ups and merge conflict resolution.

```mermaid
flowchart TB
    subgraph PersonA[Person A — Loop and CLI]
        CLI[cli.py]
        Loop[loop.py]
        Bank[context_bank.py]
    end

    subgraph PersonB[Person B — Intelligence]
        WX[watsonx_client.py]
        Gen[generator.py]
        Fix[fixer.py]
    end

    subgraph PersonC[Person C — Execution and demo]
        Runner[runner.py]
        Sample[sample-repo/]
        Demo[README + demo]
    end

    style PersonA fill:#e6f1fb,stroke:#185fa5
    style PersonB fill:#fbeaf0,stroke:#993556
    style PersonC fill:#eaf3de,stroke:#3b6d11
```

**Key idea:** dependencies between modules cross owner boundaries. That's why the shared contracts in `CONTRACTS.md` matter — each person works against the contract, not against another person's half-finished code.

---

## 5. Data flow — what travels between modules

The actual shape of the data passed at each edge. Useful when debugging integration issues.

```mermaid
flowchart LR
    Code[source code<br/><i>str</i>] --> Gen[Generator]
    Ctx[context dict] --> Gen
    Gen --> Tests[tests<br/><i>list of str</i>]

    Tests --> Runner
    Path[target path<br/><i>str</i>] --> Runner
    Runner --> Results[results<br/><i>list of dicts</i>]

    Results --> Fixer
    Code --> Fixer
    Ctx --> Fixer
    Fixer --> Patch[patch<br/><i>dict</i>]

    Patch --> Save[append to context]
    Save --> JSON[(JSON file)]
```

**Key idea:** all interfaces use plain Python types — strings, lists, dicts. No custom classes. This is intentional for a PoC: it makes mocking trivial during Sprint 1 and keeps each module debuggable on its own.

---

## 6. Build-time vs runtime

Often confused. The AI editor and IBM Bob are tools used **during the hackathon** to write the agent's code. They are **not** part of the running product. Once the PoC is built, only the CLI and watsonx.ai matter.

```mermaid
flowchart LR
    subgraph BuildTime[Build time — during the hackathon]
        Team([Team of 3]) --> Editor[AI editor<br/><i>Cursor / Claude Code</i>]
        Team --> Bob[IBM Bob<br/><i>session reports</i>]
        Editor --> Code[Agent source code]
        Bob --> Code
    end

    subgraph Runtime[Runtime — when the PoC runs]
        User([End user]) --> CLI[CLI<br/><i>python -m agent.cli</i>]
        CLI --> Agent[Agent loop]
        Agent --> Watsonx[watsonx.ai]
    end

    Code -.deployed as.-> CLI

    style BuildTime fill:#e1f5ee,stroke:#0f6e56
    style Runtime fill:#faeeda,stroke:#854f0b
```

**Key idea:** three different AI systems, three different roles, do not mix them when explaining to judges:

| Tool | Role | When it runs |
|---|---|---|
| **AI editor** (Cursor / Claude Code) | Writes the Python code of the agent | Build time only |
| **IBM Bob** | Development partner; session reports prove how you built it | Build time only |
| **watsonx.ai** | Reasoning engine inside the agent (generates tests, suggests fixes) | Runtime |

The product is the **CLI**. The AI editor disappears once the hackathon ends.

---

## Tips for using these diagrams with your AI editor (during the hackathon)

These tips apply while the team is **writing** the agent — they're for your Cursor / Claude Code / Copilot sessions, not for the running product.

- **Paste this whole file** as project context when starting a new AI editor session. The diagrams disambiguate what each module is supposed to do better than prose alone.
- **Reference diagrams by number** in prompts: "based on the sequence in section 2, implement `loop.run`".
- **Update diagrams as you go.** If the implementation drifts from the diagram, fix the diagram in the same PR. Stale diagrams are worse than no diagrams.
- **For the final demo,** export each diagram as PNG (in VS Code: right-click on the rendered preview, save as image). Drop them into your slides.
