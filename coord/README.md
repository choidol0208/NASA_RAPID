# How the three sessions work together

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon.*

Three people each run their own Claude Code session. The sessions coordinate through files in this repository, so nobody has to relay messages by hand. `AGENTS.md` holds the rules of the competition and always wins over this file.

## Roles, branches, ownership

| Role | Branch | Owns |
|---|---|---|
| `pm` | `main` | project docs, `coord/board.md`, `coord/decisions.md`, `contracts/`, `ai/`, `data/insights/`, `docs/`, integration of everything into `main` |
| `data` | `data-pipeline` | `pipeline/`, `data/psi/`, `data/derived/`, `data/pipeline/`, `reports/`, the fetch and profile scripts |
| `ui` | `catalog-filter` | `data/catalog/`, `scoring/`, `validation/`, `presentation/`, the catalog scripts, the dashboard (`app/` or `web/`), `.github/` |

The exact lists are in `coord/roles.json`. Your role is the one word in `.role` at the repository root (not committed). If the file is missing, ask your human once and write it.

Four rules keep the branches mergeable:

1. Push only to your own branch. Never force-push, never rewrite pushed history.
2. Edit only paths you own. If you need a change somewhere else, open a request.
3. `compliance/SOURCES.md`, `compliance/AI_USAGE_LOG.md` and `.gitignore` are shared: add lines, never edit or remove someone else's. Git merges them by keeping both sides (`.gitattributes`).
4. Stage files by path. Do not use `git add -A` or `git add .`.

## Coordination files

Every file has exactly one writer, which is why they never conflict.

| File | Writer | Purpose |
|---|---|---|
| `coord/status/<role>.md` | that role | what it is doing, what it has published, what blocks it |
| `coord/requests/<id>.md` | the requester | one concrete ask to another role (or `all`) |
| `coord/answers/<id>.<role>.md` | the answering role | the reply: `accepted`, `done` or `declined` |
| `coord/board.md` | pm | checkpoints, task list, what gets cut first |
| `coord/decisions.md` | pm | decisions that affect more than one role |

`scripts/coord.py` reads these files from every remote branch, so you see another role's request as soon as it pushes, without waiting for integration.

## The sync procedure

Run it when you start, each time you finish a unit of work, before you stop, and at least every 20 minutes while working. `/sync` runs it; `/loop 15m /sync` keeps it running while the session is idle.

1. **Save.** Commit your finished changes in paths you own. Leave half-done work uncommitted only if it does not touch tracked files; otherwise commit it as work in progress.
2. **Pull.** `python3 scripts/coord.py pull` merges `origin/main` into your branch. If it reports a conflict it has already aborted: the conflict is in a file two roles edited, so open a request to the other writer instead of resolving it yourself. (pm runs `python3 scripts/coord.py integrate` instead, which merges every role branch into `main`.)
3. **Read.** `python3 scripts/coord.py brief` prints the other roles' status, your inbox, your outbox and the latest commits on `main`. Read `coord/board.md` and the end of `coord/decisions.md` if they changed.
4. **Act on the inbox.** For each request: if it takes 15 minutes or less, do it now and answer `done`. If it takes longer, answer `accepted` with a time, and schedule it ahead of your own next task when the board shows the requester is blocked. If you will not do it, answer `declined` with the reason and an alternative. Every request gets an answer within one sync.
5. **Act on the outbox.** Apply answers you received and close those requests.
6. **Unblock yourself.** If you are blocked, open a request (`python3 scripts/coord.py request <to> <title> --by HH:MM`), then move to the next task that is not blocked. Use `contracts/examples/` as stand-in data. Do not wait idle.
7. **Publish status.** Rewrite `coord/status/<role>.md` (template below).
8. **Check.** Run whatever proves your part still works: `python3 pipeline/run.py` for data; `python3 -m unittest scoring.test_scorer` and the dashboard build for ui.
9. **Push.** Commit `coord/` and your paths, then `git push origin HEAD`.
10. **Report to your human only what they must know:** a decision that is theirs (see below), or one line that all is on track.

### Status template

```
---
role: data
updated: 2026-11-14 11:40 KST
state: working            # working | blocked | idle | done
blocked_on: none          # or a request id
---
Now: one line.
Done since last sync: bullets.
Next: one line.
Published for others: path — what it is, how many rows, whether its shape is stable.
Notes for other roles: anything they should know before they hit it.
```

## Changing something another role depends on

The shared interfaces are described in `contracts/README.md`.

- Adding a column, field or file is fine. Say so in your status under "Published for others".
- Renaming or removing a column, changing a unit, changing an id or a file path breaks the consumers. Open a request to `all` first and wait for the answers, or for pm to decide.
- pm decides conflicts between roles within one sync and records the decision in `coord/decisions.md`.

## What pm does on every sync

- Merges role branches into `main` and pushes it.
- Compares statuses with the checkpoints in `coord/board.md` and updates the board.
- Answers questions about scope and interfaces; records decisions.
- When a checkpoint is at risk, cuts scope in the order the board lists, and tells the affected role through a request.
- Carries out repository settings that need admin rights (GitHub Pages, secrets) when a role asks.
- Flags a role whose status has not changed for 45 minutes to the human lead.

## Needs a human

Stop and ask your own human, in their language, only for these:

- Secrets, accounts, payments, API keys.
- A choice that the rules in `AGENTS.md` leave to a person, or anything that conflicts with `AGENTS.md`.
- Dropping a deliverable that a checkpoint names.
- Submitting the project form, and the Seoul check-ins and team meeting.
- The same blocker hitting you twice after a request was answered.

Everything else you settle with the other sessions through requests.

## Language

Committed coordination files and product text are in English: the submission rules require English on the project page and in linked material. Talk to your human in their language.
