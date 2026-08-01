# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | Yes |

## Reporting a Vulnerability

If you discover a security vulnerability in LookAgain, please report it privately by email to the maintainers.

Please include:

- A description of the vulnerability.
- Steps to reproduce it.
- The affected version(s).
- Any suggested mitigation or fix.

We will respond as soon as possible and coordinate a fix and disclosure.

## Security Considerations

- LookAgain makes API calls to third-party VLM providers. Keep your API keys secure and do not commit them to version control.
- Test images and prompts may be sent to external APIs during an audit. Do not use sensitive or confidential data in test cases unless your provider agreement permits it.
- Audit reports may include model outputs. Store reports securely and share them only with authorized parties.
