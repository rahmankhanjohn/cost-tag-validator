# Contributing to cost-tag-validator

Thanks for taking the time to contribute.

## What this project is

A single-file Python CLI that checks tagging taxonomies in Terraform, Helm and YAML files against expected keys and values. Zero dependencies, MIT licence.

## Getting started

```
git clone https://github.com/rahmankhanjohn/cost-tag-validator.git
cd cost-tag-validator
python -m unittest test_cost_tag_validator -v
```

All tests should pass on Python 3.9 or newer. No install step.

## Rules of the codebase

1. **No dependencies.** Standard library only. If a feature needs a third-party package, it does not go in this repo.
None
2. **Single file.** `cost_tag_validator.py` is the whole tool. Keep it that way.
3. **Every feature needs a test.** Add a test in `test_cost_tag_validator.py` that fails without your change.
4. **Exit codes matter.** 0 = pass, 1 = fail, 2 = error. Do not break this contract.
5. **Plain English in output.** Every number carries a plain sentence explaining what it means. No jargon without a gloss.
6. **No em dashes.** Use periods or commas.

## How to contribute

1. Fork the repository.
2. Create a branch: `git checkout -b feat/your-change`.
3. Make your change. Add or update tests.
4. Run the full suite: `python -m unittest test_cost_tag_validator -v`.
5. Run the smoke test: `python cost_tag_validator.py . --report`.
6. Open a pull request with a short description of what you changed and why.

## What we are looking for

- Additional checks and validation rules
- Better heuristics for edge cases
- Additional output formats
- Documentation improvements
- Bug reports with reproduction steps

## What we are not looking for

- New dependencies
- Rewriting the tool in another language
- Features that require elevated privileges

## Reporting bugs

Open a GitHub issue with:
- The command you ran
- The output you got
- The output you expected
- Your Python version and operating system

## Code of conduct

Be direct, be specific, be kind. This is a tool for operators who are already having a hard quarter. Don't make them work harder to use it.
