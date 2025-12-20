# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it to us privately. **Do not open a public issue.**

### How to Report

Please email security concerns to: **ibegtin@dateno.io**

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to Expect

- We will acknowledge receipt of your report within 48 hours
- We will provide an initial assessment within 7 days
- We will keep you informed of our progress
- We will notify you when the vulnerability has been resolved

### Disclosure Policy

- We will work with you to understand and resolve the issue quickly
- We will credit you for the discovery (unless you prefer to remain anonymous)
- We will not disclose the vulnerability publicly until a fix is available
- We will coordinate with you on the timing of public disclosure

## Security Best Practices

When using this SDK:

1. **Validate Input**: Always validate user input before passing it to SDK methods
2. **Database Path**: Use environment variables or explicit paths rather than relying on default locations in production
3. **Error Handling**: Implement proper error handling to avoid exposing sensitive information
4. **Dependencies**: Keep dependencies up to date by regularly running `pip list --outdated`
5. **Read-Only Access**: The SDK uses read-only database connections, but ensure your database file has appropriate permissions

## Known Security Considerations

- The SDK uses parameterized queries to prevent SQL injection
- Database connections are read-only by default
- Input validation is performed on critical methods
- No network communication is performed by the SDK

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.0 → 0.1.1). We recommend keeping your installation up to date.

## Additional Resources

- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Common Weakness Enumeration (CWE)](https://cwe.mitre.org/)

