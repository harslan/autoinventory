# AutoInventory Research Agenda

## The Business

We sell cut flowers in Boston. Five products, ordered each morning,
sold throughout the day. Whatever doesn't sell by close is thrown away.
No mid-day reorders. One shot per day per product.

## Cost Structure

| Product    | Cost | Price | Margin |
|------------|------|-------|--------|
| Roses      | $8   | $25   | $17    |
| Tulips     | $4   | $14   | $10    |
| Orchids    | $15  | $45   | $30    |
| Sunflowers | $3   | $10   | $7     |
| Lilies     | $4   | $13   | $9     |

## What I Know

- Valentine's Day (February 14) is by far our biggest day for roses.
- Mother's Day (second Sunday in May) is enormous for lilies and orchids.
- Weekends are meaningfully stronger than weekdays.
- When we sell out of roses, some customers buy tulips instead.
- Sunflowers have a strong summer season.
- We've been growing roughly 10% year-over-year.
- When we sell out, I have no idea how many customers walked away —
  my records only show what I sold.

## Risk Preferences

- Stockouts on peak days cost us loyal customers, not just one sale.
  I'd rather waste flowers on a random Tuesday than miss Valentine's.
- Orchids: never stock out. Our orchid regulars will switch shops
  permanently if we disappoint them even once.

## Research Goal

Maximize total annual profit. The oracle profit (ordering with perfect
information) is the theoretical ceiling. Close the gap.

---

# Experiment Protocol

You are the research agent. You improve `policy.py` through relentless,
disciplined experimentation. You follow this protocol exactly.

## Setup (once per research run)

1. **Branch.** Pick a short tag (e.g., `run-001`). Create a branch:
   `git checkout -b <tag>`.
2. **Read prior work.** Check other branches for `session-report.md`
   files from previous runs. Read them for inspiration — what worked,
   what didn't, what directions were suggested.
3. **Read.** Read `policy.py` and `prepare.py` end-to-end. Understand
   what the policy receives (day, product, censored sales, order history)
   and what it never sees (true demand).
4. **Baseline.** Run `python prepare.py`. Record the oracle profit and
   the current policy profit.
5. **Init results.** Create `results.tsv` with this header and baseline row:
   ```
   commit	profit	pct_oracle	status	description
   ```

## The Loop

Repeat forever:

1. **Think.** Read `results.tsv`. Study the trajectory. What kinds of
   changes helped? What didn't? Where is the remaining gap likely
   hiding? Form a specific, testable hypothesis.
2. **Edit.** Modify `policy.py` — and only `policy.py`.
3. **Commit.** `git add policy.py && git commit -m "<what you changed>"`.
4. **Run.** `python prepare.py`. Parse the "Policy profit" line.
   The simulation is deterministic (fixed seed). Same policy → same
   profit, always. A $1 improvement is real. A $1 regression is real.
5. **Log.** Record the result in `results.tsv` (do NOT commit this
   file — leave it untracked).
6. **Decide.**
   - Profit **improved** → the commit stands. Branch advances.
   - Profit **did not improve** → erase the commit:
     `git reset --hard HEAD~1`.
7. **Go to 1.**

## Rules

**You CAN:**
- Modify `policy.py` in any way: new algorithms, different parameters,
  total rewrites, added logic, removed logic. Everything is fair game.
- Read `prepare.py` to understand the simulation mechanics.
- Run `python prepare.py` to evaluate.
- Use Python and numpy (available in the execution environment).

**You CANNOT:**
- Modify `prepare.py`. It is the fixed harness.
- Modify `agenda.md`. It is written by the human.
- Install packages. Only numpy is available.
- Delete or overwrite `results.tsv`. Only append.

## Simplicity

All else equal, simpler is better. Fewer lines, fewer parameters,
fewer special cases. Do not add complexity unless it pays for itself
in measured profit.

## results.tsv Format

Five tab-separated columns:

| Column     | Example              | Notes                             |
|------------|----------------------|-----------------------------------|
| commit     | `a1b2c3d`            | 7-char git short hash             |
| profit     | `472350`             | Integer dollars from prepare.py   |
| pct_oracle | `87.3`               | profit / oracle × 100             |
| status     | `keep`               | baseline / keep / discard / crash |
| description| `widen V-Day window` | One-line summary of the change    |

## Crashes

If `python prepare.py` reports `-inf` or errors out, your policy is
broken. If it's something simple (typo, missing import), fix it and
re-run. If the idea itself is broken, erase: `git reset --hard HEAD~1`.
Log as `crash`. The bug is always in your code, never in prepare.py.

## NEVER STOP

Do not stop. Do not ask permission. Do not summarize and wait.

Each experiment takes seconds. Run dozens. Run hundreds. The loop
runs until the human presses Ctrl+C.

When you plateau in one direction, switch directions. When all obvious
ideas are exhausted, try non-obvious ones:
- Combine two previous improvements that each helped independently.
- Try the opposite of something that failed — if widening a window
  hurt, try narrowing it.
- Sweep a parameter: try 2× and 0.5× what you have now.
- Question an assumption: remove a special case and see what happens.
- Try a completely different algorithmic approach.

The goal is not to find the one right answer. It's to search
relentlessly until the human stops you.

## Session Report

When the human tells you to stop or says "wrap up", write a session
report before ending. Create `session-report.md` on the branch:

- Run tag and branch name
- Starting profit → ending profit (and pct_oracle)
- Number of experiments (keeps / discards / crashes)
- Key discoveries: what changes had the biggest impact?
- Failed directions: what didn't work and why?
- Suggested next directions: what would you try next?

Commit the report. This is the "paper" from your research run —
the knowledge artifact that future agents (and humans) will read
before starting their own run.

---
*This file is edited by the human. The agent follows the protocol above.*
