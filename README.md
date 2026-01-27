# pre-commit-hooks-submodules

submodules-related hooks for [pre-commit]

## Usage

Write your `.pre-commit-config.yaml` as below.

```yaml
repos:
  - repo: https://github.com/paulsohn/pre-commit-hooks-submodules
    rev: v0.1.0
    hooks:
      - id: check-gitmodules
```

## Hooks available

### check-gitmodules

Check `.gitmodules` for proper submodule configuration:

- `name` matches with submodule path.
- At lease one of the following attributes exist: `branch = <branch>` or `update = none`.
