# Notes for LLM contributors

## Rule zero: prove it works before opening the PR

**Your job is to deliver code that is proven to work.** If you
have not proven the change works, it is not time to open the PR
yet. "It compiles", "type checks pass", and "the diff looks
right" are not proof. Proof is: the relevant tests run locally
and pass, the new behaviour is exercised by a test you added or
extended, and any user-visible path you touched has been
executed end-to-end. If you cannot run the suite in your
environment, say so explicitly in the PR body rather than
implying coverage you did not actually achieve. Opening a PR
that turns out not to work wastes the reviewer's time and is
the single fastest way to lose trust on this repo.

The rest of this document covers how to dress up that proven
change for review. None of it matters if rule zero is not met.

---

Read this before opening a pull request against
`aio-libs/aiohttp-remotes`. The rules below are not optional. If
you are about to skip a section because it sounds boilerplate,
that is exactly the section to re-read.

Human-facing contributor docs for news fragments live in
[CHANGES/README.rst](CHANGES/README.rst); this file is the short
orientation for agents.

## What this project is

`aiohttp-remotes` is a set of `aiohttp.web` middlewares that
restore the real client address, scheme and host when the server
runs behind a reverse proxy (`Forwarded`, `X-Forwarded-*`,
Cloudflare), plus a few related helpers (allowed hosts, basic
auth, HTTPS enforcement). It is security sensitive: a mistake in
header parsing lets a client spoof its IP address or scheme.

Useful entry points:

| Path                             | What                                              |
| -------------------------------- | ------------------------------------------------- |
| `aiohttp_remotes/__init__.py`    | public exports, `setup()` helper, `__version__`   |
| `aiohttp_remotes/abc.py`         | `ABC` base class shared by all middlewares        |
| `aiohttp_remotes/forwarded.py`   | `ForwardedRelaxed` / `ForwardedStrict` (RFC 7239) |
| `aiohttp_remotes/x_forwarded.py` | `XForwardedRelaxed` / `XForwardedFiltered` / `XForwardedStrict` |
| `aiohttp_remotes/cloudflare.py`  | `Cloudflare` trusted-network middleware           |
| `aiohttp_remotes/allowed_hosts.py` | `AllowedHosts`                                  |
| `aiohttp_remotes/basic_auth.py`  | `BasicAuth`                                       |
| `aiohttp_remotes/secure.py`      | `Secure` (HTTPS redirect, HSTS and friends)       |
| `aiohttp_remotes/utils.py`       | trusted-hosts parsing helpers                     |
| `aiohttp_remotes/exceptions.py`  | `RemoteError` and its subclasses (`UntrustedIP`, `TooManyHeaders`, ...) |
| `tests/`                         | pytest suite                                      |
| `CHANGES/`                       | towncrier news fragments, one per PR              |
| `docs/`                          | Sphinx docs source (`docs/index.rst`, `docs/api.rst`) |

The package is built with `flit`; the version lives in
`aiohttp_remotes/__init__.py`.

## Pull request rules

These are the rules agents most often violate. Treat them as
mandatory.

### 1. Use the aio-libs pull request template

`aiohttp-remotes` follows the standard `aio-libs` PR template.
Even though the repo does not ship its own
`.github/PULL_REQUEST_TEMPLATE.md`, maintainers expect every PR
body to follow this exact structure. Do not invent your own
`## What / ## Why / ## How / ## Testing` layout; that is the
marker that the PR was written by an agent without reading the
conventions.

Fill out the template verbatim, like so:

```markdown
<!-- Thank you for your contribution! -->

## What do these changes do?

<short prose describing the change>

## Are there changes in behavior for the user?

<yes or no, plus a sentence if yes>

## Is it a substantial burden for the maintainers to support this?

<no, plus a sentence on why if relevant>

## Related issue number

Fixes #NNNN
<!-- or a bare reference if the change is related but does not close -->

## Checklist

- [x] I think the code is well written
- [x] Unit tests for the changes exist
- [x] Documentation reflects the changes
- [x] Add a new news fragment into the `CHANGES/` folder
```

Tick the boxes that actually apply. If a row does not apply
(e.g. CI-only change with no tests), write `N/A` next to it
rather than silently leaving it blank.

### 2. Add a CHANGES fragment

Every user-visible PR needs a towncrier news fragment in
`CHANGES/`, named `<pr_number>.<category>.rst`. The project uses
the towncrier default categories (see
[CHANGES/README.rst](CHANGES/README.rst)):

| Category  | When to use                                                    |
| --------- | -------------------------------------------------------------- |
| `feature` | new public API or behaviour                                    |
| `bugfix`  | corrects undesired behaviour                                   |
| `doc`     | documentation changes                                          |
| `removal` | deprecations and removals of an existing feature or behaviour  |
| `misc`    | internal changes: CI, tests, build, dev environment            |

Conventions for the fragment body:

- Use the past tense (`Fixed`, `Added`, `Dropped`), since it is
  read as a "what changed since the previous release" digest.
- Use reStructuredText, not Markdown.
- Do not include the issue or PR number in the body; towncrier
  adds it automatically from the filename.
- Sign with `-- by :user:\`github-handle\`` at the end.

Example:

```rst
Fixed ``XForwardedStrict`` to reject an empty ``X-Forwarded-For``
element instead of treating it as a trusted hop
-- by :user:`github-handle`.
```

Pick the number for the fragment filename as follows:

- **If the change has a linked issue, name the fragment after
  the issue number** (e.g. `CHANGES/123.bugfix.rst` for a fix
  that closes `#123`).
- **If there is no linked issue,** either open the PR first and
  add the fragment as a follow-up commit using the assigned PR
  number, or guess the next PR number (scan
  `gh pr list --state all --limit 5` for the current top of the
  range) and rename in a follow-up commit if the guess was off.

### 3. Open the PR as a draft, and leave it that way

Use `gh pr create --draft`. **Every LLM-authored submission
must be fully reviewed by a human before it is marked ready
out of draft, with no exceptions.** That review is the
responsibility of the person running the agent, not of the
project maintainers. Do not mark the PR ready yourself, and do
not request reviewers from the agent session; the human who
reviewed the change and flipped it out of draft is the one who
routes it.

### 4. Disclose the agent, do not advertise it

Disclosure is required, advertising is not welcome. Put one
plain line at the bottom of the PR body naming the agent that
drafted the change, for example:

```
Drafted with <agent name and version>; reviewed by <human handle>.
```

That single line is enough. Beyond that:

- **No `Co-Authored-By:` trailers** for an LLM or any AI tool,
  in commits or in the PR body. Attribution goes to the human
  who reviewed the change.
- **Agent output goes in a footer below the PR summary, ideally
  in a collapsed `<details>` block.** The template sections come
  first and read like a human wrote them. Anything the agent
  wants to surface for reviewers (test logs, lint output, branch
  hygiene notes) goes underneath:

  ```markdown
  <details>
  <summary>Agent run details (optional, for reviewers)</summary>

  Tests: <command and result>
  Lint: <command and result>
  </details>
  ```

- No `🤖`, `✨`, `🚀` emoji decoration in commit messages, PR
  titles, PR bodies, or news fragments. Project style is plain
  prose.
- Commit messages and PR prose should read as if a human
  contributor wrote them. Specifically:
  - **No em-dashes (`—`)** and no dashes used as sentence
    separators (`foo - bar`). Use a semicolon or a comma.
  - No "Let me", "I'll", or first-person narration of what the
    agent did. Describe the change, not the author.
  - No filler sections ("Overview", "Summary of changes",
    "Key takeaways") on top of the template.

### 5. Keep the PR body short

A couple of sentences per template section is plenty. If the
change is non-obvious, a short reproducer or a paragraph on root
cause is welcome. Long, multi-section essays with bolded
sub-headings are not the style here.

### 6. Commit hygiene

- One logical change per PR. If a refactor and a bugfix are
  bundled together, split them.
- Pre-commit auto-fixes (black, isort, pyupgrade, yesqa,
  trailing-whitespace, end-of-file-fixer) run on commit and
  rewrite files in place; when a hook rewrites a file the commit
  aborts, so re-stage and commit again.
- The repo does not use Conventional Commits. Landed subjects are
  short imperative prose (e.g. `Drop Python 3.9-3.10, support
  3.15`, `Modernize pyproject.toml`). Match that style; do not
  force `feat:` / `fix:` prefixes.

## Tests and lint

Install dev deps and run the suite:

```bash
make setup       # pip install -r requirements/dev.txt, pre-commit install, flit install -s
make test        # pytest tests
make lint        # pre-commit on all files, then mypy --strict
```

CI runs `make lint` once and `make test` across every supported
Python version (see `.github/workflows/ci.yml`). Both must pass
locally before pushing.

The suite runs with `filterwarnings = error`, so a new warning
(deprecation, unclosed resource) fails the test. Fix the cause;
do not add a blanket ignore.

### Every line in a test must be covered

Coverage is collected with branch coverage and reported to
Codecov; it applies to test code too, not just
`aiohttp_remotes/`. A test that contains a branch or statement
the suite never reaches is dead code.

- Drive the fixture deterministically so both arms of any
  conditional are hit, or drop the conditional and assert the
  single shape you actually set up.
- Do not add `raise TypeError("must not be invoked")` guards
  inside stubs the test installs; if the stub is never meant to
  fire, omit it or assert at the call site that it did not.
- Prefer `monkeypatch` (which auto-reverts) over hand-rolled
  save/restore blocks.

### Security-sensitive changes

Any change to how a header is parsed or which peers are trusted
needs tests for the hostile case as well as the happy path:
spoofed headers from an untrusted peer, too many or too few hops,
malformed values, IPv6 addresses. A middleware that silently
accepts a forged `Forwarded` or `X-Forwarded-For` value is a
vulnerability, not a bugfix candidate for later.

## Documentation

User-visible API changes need a docs update in `docs/index.rst`
or `docs/api.rst`. `make doc` builds the docs locally.

## Things not to do

- Do not open a PR for code you have not proven works (see
  _Rule zero_ at the top of this file).
- Do not invent a `## What / ## Why / ## How / ## Testing` PR
  body; use the aio-libs template above.
- Do not skip the `CHANGES/` fragment "because the change is
  small". Even a one-line bugfix needs one.
- Do not add `Co-Authored-By` trailers for LLM tools, in either
  commits or the PR body.
- Do not mix agent-generated test summaries or pipeline reports
  into the template sections. Put them in a collapsed
  `<details>` footer below the PR summary instead.
- Do not use em-dashes or sentence-separating dashes in PR prose
  or commit messages.
- Do not commit build output (`dist/`, `docs/_build/`,
  `htmlcov/`, `.coverage`).
- Do not leave unreachable lines in tests; see _Every line in a
  test must be covered_ above.
- Do not mark the PR ready for review yourself, and do not
  request reviewers from the agent session.
