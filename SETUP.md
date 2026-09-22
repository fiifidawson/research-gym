# Setting up a fresh copy

One-time, maintainer only. Everything already works locally; these steps give it a GitHub home.

## 1. Push

```bash
gh repo create <org-or-you>/research-gym --private --source=. --push
```

Nothing in here is secret. The skills survey is not in the repo and is ignored by `.gitignore`.

## 2. Turn on Actions and Pages

- Settings → Pages → Source: **GitHub Actions**
- Settings → Actions → General → Workflow permissions: **Read and write** (the check needs this to
  post its comment)

Push to `main` once; the site deploys and gives you a URL.

## 3. Replace the placeholders

Now you know the site URL:

```bash
grep -rl REPLACE-ME --include='*.md' --include='*.json' --include='*.yml' --include='CODEOWNERS' . | xargs sed -i 's|REPLACE-ME|<org-or-you>|g'
```

Check nothing is left: `grep -rn REPLACE-ME . | grep -v '\.git/'`

Then put real handles in `.github/CODEOWNERS`, either teams or a list:

```
submissions/          @handle1 @handle2 @handle3
modules/*/checks.py   @handle1
```

## 4. Set SITE_URL

Settings → Secrets and variables → Actions → Variables:

```
SITE_URL = https://<org-or-you>.github.io/research-gym/
```

Optional. It adds a playground link to each check comment.

## 5. Protect main

Settings → Rules → Rulesets → New branch ruleset, targeting `main`:

- Require a pull request, **1 approval**
- Require status checks: **`check`** and **`ruff`**
- Require branches up to date

Give yourself a bypass so you can unstick people.

## 6. Give everyone write access

Collaborators or a team with Write. Everyone works on branches in this repo, which is what lets the
check post comments and lets people read each other's merged work.

## 7. Do module 00 yourself first

Ten minutes, and you'll have an example pull request to point at. There's a profile at
`submissions/arnolfokam/00-onboarding/profile.json` — edit the `here_for` line, it was written from
a survey answer rather than by you.

## Running the week

- Monday: module opens, post the link to its `TASK.md`.
- Friday: pull requests in.
- Rotate reviews. Pair someone who hasn't reviewed with someone who has.
- End of week: fifteen minutes on one thing that was hard. A debugging session, not a demo.

## Adding modules

02 onwards are stubs. Give them away rather than writing them all yourself — the person who writes a
module learns it twice. Shape is in
[CONTRIBUTING.md](CONTRIBUTING.md#writing-a-module); module 01 is the example.

The rule that matters: write the reference solution, confirm it passes, then break it three ways and
read the failure messages as if you were stuck.
