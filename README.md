# VANRAKSHA AI — SIH 2026

AI-Powered Forest Intelligence & Early Warning System  
**Tagline:** From Detection to Decision

This repository currently holds the **engineering master plan**. Implementation follows atomic TODOs one at a time.

## Frontend

The Command Centre lives in [`frontend/`](./frontend) — Next.js App Router, TypeScript, Tailwind CSS v4, `motion` for animation.

```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
```

`npm run build` runs the production build; `npx tsc --noEmit` type-checks without emitting.

## Planning documents

| File | Contents |
|------|----------|
| [VANRAKSHA_AI_COMPLETE_ROADMAP.md](./VANRAKSHA_AI_COMPLETE_ROADMAP.md) | Combined roadmap + all atomic TODOs (VR-001 … VR-096) |
| [docs/IMPLEMENTATION_ROADMAP.md](./docs/IMPLEMENTATION_ROADMAP.md) | Architecture, stack, licenses, risks, definition of done |
| [docs/TODOS.md](./docs/TODOS.md) | Atomic implementation tasks for OpenCode |

**Next implementation task:** `TODO VR-001` in `docs/TODOS.md`.
