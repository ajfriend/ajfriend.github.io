# Claude Code Guidelines

## Fetching GitHub PR content

To read code from a GitHub PR, download the `.diff` to a temp file, then use local tools:

```bash
curl -sL "https://github.com/OWNER/REPO/pull/NUMBER.diff" > /tmp/pr-NUMBER.diff
```

Then use Grep/Read on the local file:

```bash
grep -A 50 "typedef struct Arc" /tmp/pr-1113.diff
```

Benefits:
- Download once, search many times
- Use Grep tool with context flags (-A, -B, -C)
- Use Read tool for specific line ranges
- No repeated network requests

Don't bother with:
- WebFetch on GitHub HTML pages (content gets mangled)
- Trying to guess raw file URLs for unmerged PRs
- GitHub API for file contents (adds complexity)
