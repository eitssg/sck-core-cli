# Copilot Instructions (Submodule: sck-core-cli)

- Tech: Python package (CLI).
- Precedence: Use this file first; otherwise, root: `../../.github/copilot-instructions.md`.
- Conventions: Follow Python backend style in `../sck-core-ui/docs/backend-code-style.md` when interacting with S3/Lambda/etc.
- API envelopes: If CLI consumes core APIs, expect `{ status, code, data, metadata, message }` envelopes.
- Auth/session: Respect UI auth conventions if simulating UI flows.
- On conflicts, prefer local and raise a contradiction notice.

## Google Docstring Requirements
**MANDATORY**: All docstrings must use Google-style format for Sphinx documentation generation:
- Use Google-style docstrings with proper Args/Returns/Example sections
- Napoleon extension will convert Google format to RST for Sphinx processing
- Avoid direct RST syntax (`::`, `:param:`, etc.) in docstrings - use Google format instead
- Example sections should use `>>>` for doctests or simple code examples
- This ensures proper IDE interpretation while maintaining clean Sphinx documentation

## Contradiction Detection
- Compare prompts against backend conventions in `../sck-core-ui/docs/backend-code-style.md` and root precedence in `../../.github/copilot-instructions.md`.
- If CLI UX mirrors UI flows, also check `../sck-core-ui/docs/auth-session-and-storage.md`.
- If a prompt conflicts, reply as:
  1. Warning quoting the conflicting instruction and source rule.
  2. Options to align or update docs.
  3. Example: "CLI proposal to store tokens in localStorage conflicts with UI auth docs; use memory or sessionStorage per spec."

## Standalone clone note
If you cloned this submodule by itself, use:
- UI/backend conventions: https://github.com/eitssg/simple-cloud-kit/tree/develop/sck-core-ui/docs
- Root Copilot guidance: https://github.com/eitssg/simple-cloud-kit/blob/develop/.github/copilot-instructions.md

