# CampusHire Authentication

CampusHire no longer uses email OTPs or SMTP for registration/login.

- Candidate registration activates the account immediately.
- Recruiter registration activates the account immediately.
- Login accepts username or email plus password.
- No verification-code page is required.
- No SMTP credentials are required to run the project.

If an account password must be reset during the demo, use the Django admin to set a new password rather than relying on an email service.
