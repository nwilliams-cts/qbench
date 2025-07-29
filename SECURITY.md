# Security Policy

## Supported Versions

We actively support the following versions of the QBench SDK with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in the QBench SDK, please follow these steps:

### 1. Do NOT Create a Public Issue

Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report Privately

Send an email to **nwilliams@smithers.com** with the following information:

- **Subject**: "Security Vulnerability in QBench SDK"
- **Description**: A clear description of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact**: Description of the potential impact
- **Suggested Fix**: If you have suggestions for fixing the issue

### 3. Response Timeline

- **Initial Response**: We will acknowledge receipt of your report within 48 hours
- **Assessment**: We will assess the vulnerability within 5 business days
- **Resolution**: Critical vulnerabilities will be addressed within 14 days, others within 30 days
- **Disclosure**: We will coordinate with you on responsible disclosure timing

## Security Best Practices

When using the QBench SDK, please follow these security best practices:

### API Credentials

- **Never commit API keys or secrets** to version control
- Store credentials securely using environment variables or secure credential management systems
- Rotate API keys regularly
- Use the principle of least privilege for API access

```python
# ✅ Good: Use environment variables
import os
import qbench

qb = qbench.connect(
    base_url=os.getenv("QBENCH_BASE_URL"),
    api_key=os.getenv("QBENCH_API_KEY"),
    api_secret=os.getenv("QBENCH_API_SECRET")
)

# ❌ Bad: Hard-coded credentials
qb = qbench.connect(
    base_url="https://example.qbench.net",
    api_key="your_actual_key_here",  # Never do this!
    api_secret="your_actual_secret_here"  # Never do this!
)
```

### Network Security

- Always use HTTPS endpoints for QBench instances
- Validate SSL certificates in production environments
- Consider using VPN or private networks for sensitive data access
- Implement proper timeout settings to prevent hanging connections

### Data Handling

- Validate all input data before sending to the API
- Sanitize data received from the API before processing
- Implement proper error handling to avoid information disclosure
- Log security-relevant events appropriately (without sensitive data)

### Dependencies

- Keep the QBench SDK updated to the latest version
- Regularly update all dependencies to patch known vulnerabilities
- Use tools like `pip-audit` to scan for vulnerable dependencies

```bash
# Check for vulnerable dependencies
pip install pip-audit
pip-audit
```

#### Automated Security Scanning

This repository is configured with automated security scanning to ensure dependencies remain secure:

- **OSV Database Scanning**: On each commit, the package dependencies are automatically scanned against the [Open Source Vulnerabilities (OSV) database](https://osv.dev/) using Python's `safety` package
- **Continuous Monitoring**: Security reports are generated and reviewed for every code change
- **Proactive Updates**: Vulnerable dependencies are identified and updated promptly based on scan results

This automated scanning provides an additional layer of security beyond manual dependency management.

## Vulnerability Assessment

We regularly assess the security of the QBench SDK through:

- Static code analysis
- Dependency vulnerability scanning
- Security-focused code reviews
- Regular security updates

## Security Features

The QBench SDK includes the following security features:

- **Secure Authentication**: Uses API key and secret authentication
- **HTTPS Enforcement**: All communications use secure HTTPS connections
- **Input Validation**: Basic validation of API parameters
- **Error Handling**: Secure error handling that doesn't expose sensitive information
- **Timeout Protection**: Configurable timeouts to prevent hanging requests

## Third-Party Dependencies

This project uses third-party dependencies. We monitor these dependencies for security vulnerabilities and update them promptly when security patches are available.

Current major dependencies:
- `requests`: For HTTP communication
- `urllib3`: HTTP client library (dependency of requests)

## Contact

For security-related questions or concerns that are not vulnerabilities, you can:

- Email: nwilliams@smithers.com
- Include "QBench SDK Security" in the subject line

## Acknowledgments

We appreciate the security research community and will acknowledge researchers who responsibly disclose vulnerabilities (with their permission).

---

**Note**: This security policy applies to the QBench SDK. For security issues related to the QBench LIMS platform itself, please contact QBench support directly.
