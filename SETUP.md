# arlecchino_os — setup

Everything about this profile comes from `config.yaml`.
The generator never contains personal data.

```
config.yaml  →  scripts/generate.py  →  output/*.svg  →  README.md
```

Regenerate at any time:

```bash
python scripts/generate.py
```

Run the test suite after changing the generator:

```bash
python tests/test_generator.py
```

---

## Your part (the stuff left as placeholders)

**1. The portrait.**
Drop any image into `assets/portrait/` — `.png`, `.jpg`, or `.webp`.
The newest file there wins, so swapping identities is a file drop.
Give it the highest quality version you have; the generator crops it to
the frame and compresses it down to a retina-sharp, lightweight copy.
Portraits with the face in the upper-middle work best (it centre-crops).

**2. Your GitHub username.**
`config.yaml` → `identity.github_username`, and the github URL under
`contact.links`. Both currently say `kumar-butcha` as a placeholder.

**3. Turn on live data** — after the repo exists on GitHub:

```yaml
data:
  github_api: true
```

Locally it will use anonymous API calls (60/hour, plenty). In Actions it
uses the built-in `GITHUB_TOKEN` automatically. If the API is ever
unreachable the profile still builds, just without live numbers.

**4. Replace the placeholder content** — `skills`, `timeline`, and the
three `hidden` blocks are written in your voice but from my guesses.
Rewrite them as yours.

You do **not** need to touch `projects:`. Once live data is on, the
explorer is built from your real repositories every 6 hours: forks
dropped, ranked by stars then most recent push, top 8 shown, with each
repo's own description, language, topics and star count. A repo is
labelled `active`, `dormant` (nothing pushed in
`data.active_within_days`, default 90) or `archived`. Ship a new repo
and it appears on its own.

Two things that make those cards read well, both set on GitHub itself:
give each repo a **description**, and add a few **topics** — the topics
become the stack chips, falling back to the repo's main language.

The `projects:` list in the config is only a fallback for when the API
is unreachable, so the panel never disappears from an offline build.

---

## Making it a different operating system

Nothing about the OS's personality is baked into the generator. The
`labels:` block in `config.yaml` holds every piece of chrome text —
panel names, the shell prompt, the command lines, the footers, the
"you found it" whisper, even the EOF marker. Rename them and the same
code renders a completely different system.

Anything in `{braces}` is filled in for you: `{handle}`, `{os}`,
`{version}`, `{count}`, and — when live data is on — `{repos}`,
`{stars}`, `{followers}`. An unknown token is left alone rather than
breaking the build.

The design system itself stays fixed on purpose — canvas width, corner
radius, hairlines, fonts, animation timings, section order. That's what
keeps eight separate SVGs feeling like one operating system instead of
eight cards.

A worked example of a second persona lives in `examples/atlas.yaml` —
different name, colours, panel names, and content, built by this same
generator:

```bash
python scripts/generate.py --config examples/atlas.yaml --out examples/output --readme examples/README.md
```

---

## Publishing

The profile renders on your GitHub profile page when it lives in a repo
named exactly the same as your username.

```bash
git init
git add -A
git commit -m "arlecchino_os"
git branch -M main
git remote add origin https://github.com/<username>/<username>.git
git push -u origin main
```

Then in the repo: **Settings → Actions → General → Workflow permissions
→ Read and write**, so the scheduled regeneration can commit.

`.github/workflows/generate.yml` reruns the generator every 6 hours, so
live data stays fresh and the daily rotations (featured project, secret
fortune) keep the profile changing between visits.

---

## Design rules this project holds itself to

1. The hero is sacred — never sacrificed for another feature.
2. The portrait is the identity, never a decoration.
3. It must feel alive; static is the exception.
4. Everything belongs to one OS — no disconnected cards.
5. Luxury over complexity.
6. Design decisions come before engineering decisions.
7. Every feature must make a visitor say "wow" faster.
8. Implementation constraints shape *how* we build the vision,
   never *what* the vision is.
