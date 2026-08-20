# CampusHire Test Suite

The project contains **44 real Django/Python tests** under the candidate and recruiter apps.

Run the full suite from the project root:

```powershell
python manage.py test
```

The suite covers:

- resume skill extraction
- experience extraction
- project and education extraction
- keyword/tag generation
- ATS skill matching and percentage calculation
- PDF/DOCX parser behavior
- candidate registration/login
- candidate job-detail privacy before application
- resume-based application and ATS scoring
- candidate profile persistence
- recruiter authentication
- recruiter-owned job visibility
- recruiter ownership restrictions on job details/editing
- recruiter application isolation and status security

There are no standalone `print()`-based `test_*.py` scripts. Every discovered test is a Django `TestCase` or `SimpleTestCase` method.

## Expected result

The test discovery count is **44 tests**. The command above should finish with a clean `OK` after dependencies are installed.
