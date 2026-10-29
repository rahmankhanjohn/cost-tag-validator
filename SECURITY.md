# Security Policy

## Supported versions

Only the latest release on `main` is supported. Older releases receive no security fixes.

## Reporting a vulnerability

Do not open a public issue for security reports.

Email rahman.khan.john@gmail.com with:
- A description of the vulnerability
- Steps to reproduce
- The affected version or commit
- Any known workarounds

You will receive a response within 72 hours. If the report is confirmed, a fix will be released and you will be credited (unless you prefer otherwise).

## Scope

This project is a CLI tool that runs locally and reads files you point it at. It makes no network calls except:

- None. The tool reads local files only.

## What is out of scope

- Vulnerabilities in the Python runtime or Go toolchain
- Issues caused by running the tool on untrusted input without understanding what it does
- Social engineering of the maintainer

## Disclosure policy

Coordinated disclosure. The fix ships first, the advisory follows within 30 days.
