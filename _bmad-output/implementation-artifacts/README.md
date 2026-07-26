# BMAD implementation-artifacts (reference)

This folder holds **BMAD Method implementation-phase** examples for Agentic Target ID.

## What belongs here

| Artifact | Purpose |
| --- | --- |
| `sprint-status.yaml` | Sprint / epic / story status board |
| `stories/*.md` | Per-story completion records (ACs pointer, commits, file list) |

**Canonical requirements** still live in `_bmad-output/planning-artifacts/` (brief, PRD, architecture, epics).

## Why these files exist

V1 was built largely in Cursor task-mode against `epics.md`. For BMAD mastery and as a **master reference repo** (without relying on Kiro), story completion was **retroactively recorded** here from git history so you can see what idiomatic implementation-artifacts look like for **all** V1 + Epic L stories.

## Counts

- Epic 1–6 stories: **23** (`1.1`–`6.4`)
- Epic L stories: **9** (`L.1`–`L.9`)
- Total story files: **32**

## Usage

- Read `sprint-status.yaml` for the board.
- Open any `stories/{id}-*.md` for a completed-story example.
- For new work, prefer `bmad-dev-story` so future stories are written live into this folder.
