# Loopr — Hackathon Statement

We built **Loopr** — a recursive AI coding agent that doesn't just find bugs, it fixes them, remembers them, and gets smarter every run.

The problem with most AI coding tools is simple: they generate tests once and stop. They don't fix what they find. They don't remember what they already tried. Every execution starts from zero.

Loopr changes that in three major ways.

## 1. It actually fixes code instead of just reporting problems

Most tools hand developers a report and leave the work to them. Loopr generates a colored diff, proposes the fix, and can apply it directly to the codebase. The repository improves automatically instead of just collecting annotations.

## 2. Loopr has persistent memory across runs

We built a context bank that stores previous bugs, failed attempts, and successful fixes. That means run two is smarter than run one. The system avoids repeating the same failed strategies and continuously improves its testing and repair decisions over time.

## 3. Loopr is recursive by design

It doesn't stop after one pass. It loops through the repository until tests pass or iteration limits are reached. Each cycle re-reads the updated code, regenerates tests, evaluates failures, and tries again. That makes Loopr more than a test generator — it behaves like an autonomous engineering agent.

## How is this different from Claude Code or other coding assistants?

Loopr is a testing agent. You point it at a repo and walk away. It autonomously generates tests, runs them, fixes failures, and loops. Memory is built-in by design — the context bank is the whole point. And it's single purpose: make your code pass tests, period.

The key difference is that **Claude Code augments a developer. Loopr replaces a specific workflow entirely** — the "write tests → run → fix → repeat" loop that every developer does manually every day. Claude Code is like having a smart colleague sitting next to you. Loopr is like having a QA engineer who works overnight, fixes everything, and leaves you a report in the morning.

## The IBM stack behind it

What makes this especially exciting is the IBM stack behind it.

We built the system using IBM technologies end-to-end. **IBM watsonx.ai Granite** models power the runtime reasoning, test generation, and repair suggestions. **IBM Bob** acted as the development partner that understood the repository structure, planned modules, and accelerated implementation.

It's worth noting that Loopr was itself built using IBM Bob — so we're showcasing Bob's ability to produce a working agentic product, which is exactly what the hackathon theme asks for. The tool demonstrates its own premise.

And we designed the experience to be simple for developers: installable with a single command and runnable on any repository immediately.

---

The bigger idea here is that software testing shouldn't be static anymore. AI agents shouldn't just identify problems — they should iteratively solve them, learn from them, and improve over time.

That's what Loopr does.

> **Loopr is a recursive AI agent that fixes bugs, remembers failures, and gets smarter every run.**