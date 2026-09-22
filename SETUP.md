# Setting it up (maintainer, once)

Everything works locally already. These are the steps that need a real GitHub repo behind them.
Fifteen minutes, and it only happens once.

## 1. Push it

```bash
gh repo create <org-or-you>/research-gym --private --source=. --push
```

Private to start is fine; make it public whenever you like. Nothing in here is secret — **and
nothing in here is the survey**, which stays outside the repo and is ignored by `.gitignore`.

## 2. Replace the placeholders

Several files carry a `REPLACE-ME`:

| File | Change it to |
|---|---|
| `docs/data/curriculum.json` → `repo` | the repo URL |
| `.github/ISSUE_TEMPLATE/config.yml` | the same, in both links |
| `.github/CODEOWNERS` | real handles or real teams |
| `README.md`, `CONTRIBUTING.md`, the `TASK.md`s | the GitHub Pages URL, in links to the site |

Once Pages is on (step 3) and you know the site URL, swap the rest in one go:

```bash
grep -rl REPLACE-ME --include='*.md' --include='*.json' --include='*.yml' --include='CODEOWNERS' . | xargs sed -i 's|REPLACE-ME|<org-or-you>|g'
```

Then check nothing is left: `grep -rn REPLACE-ME . | grep -v '\.git/'`

For `CODEOWNERS`, either make two GitHub teams or just list handles:

```
submissions/          @fasseu @blessing @fiifi @arnolfokam
modules/*/checks.py   @arnolfokam
```

The reviewers list starts with the four people who said in the survey they could already review
someone else's code. Everyone else joins after module 05 — that is the intended promotion, and it is
worth saying out loud when you announce it.

## 3. Turn on Actions and Pages

- **Settings → Pages → Source: GitHub Actions.** The `Site` workflow does the rest.
- **Settings → Actions → General → Workflow permissions: Read and write.** The check needs this to
  post its comment.
- Push once to `main`; the site deploys and gives you a URL.

## 4. Tell the check where the site is

**Settings → Secrets and variables → Actions → Variables → New repository variable:**

```
SITE_URL = https://<org-or-you>.github.io/research-gym/
```

Optional — it only adds the "practise in your browser" link to each comment.

## 5. Protect `main`

**Settings → Rules → Rulesets → New branch ruleset**, targeting `main`:

- Require a pull request before merging — **1 approval**
- Require status checks to pass — **`check`** (from Submission check) and **`ruff`**
- Require branches to be up to date before merging

This is what makes the review real rather than optional. Allow yourself a bypass if you want to be
able to unstick people.

## 6. Give everyone write access

Collaborators, or a team with Write. Everyone works on branches in this one repo — that is what lets
the check post comments, and what lets everyone read everyone else's solutions after a merge.

## 7. Do module 00 yourself, first

Seriously. You will find out in ten minutes whether the comment reads well, and you will have an
example pull request to point at when you announce it. There is a profile already at
`submissions/arnolfokam/00-onboarding/profile.json` built from your survey answer — **edit the
`here_for` line so it is actually yours.**

## Running the week

- Monday: the module opens. Announce it with a link to its `TASK.md`.
- Friday: pull requests in.
- Reviews are the point. Rotate them, and pair someone who has never reviewed with someone who has.
- End of the week: fifteen minutes together on one thing that was hard. Not a demo — a debugging
  session, ideally on somebody's failing check.

## When you want the next module

Modules 02 onward are stubs. Writing one is the best way to learn the material twice, so give them
away rather than writing them all yourself. The shape is in
[CONTRIBUTING.md § Writing a module](CONTRIBUTING.md#writing-a-module), and module 01 is the worked
example — a `TASK.md`, a `starter/`, a `checks.py`, and `tests/test_module.py` copied verbatim.

The one rule that matters: **write the reference solution, confirm it passes, then break it three
ways and read the failure messages as if you were stuck.** If a message does not tell you what to do
next, the check is not finished.
