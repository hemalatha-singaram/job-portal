# CampusHire Demo Setup

After installing requirements and running migrations, populate the presentation data with:

```powershell
python manage.py clear_and_repopulate
```

This creates:

- 5 recruiter accounts
- 10 candidate accounts
- 10 jobs visible to candidates
- 10 demo applications on the first recruiter's main job
- ATS scores ranging from 96 down to 18, including three 80+ candidates

## Presentation recruiter

Username: `john_recruiter`

Password: `RecruiterPass123!`

This recruiter owns the main demo job **Python Django Developer** and has 10 applications with varied ATS scores.

## Demo candidates

Candidate usernames include:

- `alex_candidate`
- `priya_candidate`
- `sophia_candidate`
- `rahul_candidate`
- `ananya_candidate`
- `james_candidate`
- `meera_candidate`
- `arjun_candidate`
- `neha_candidate`
- `vikram_candidate`

Candidate password: `CandidatePass123!`

## Demo ATS scores

The main demo job has applications with these scores:

`96, 91, 87, 84, 81, 76, 68, 57, 39, 18`

The first three are marked **Shortlisted**, one is **Interview**, and the remaining applications have mixed statuses for a realistic ranking/filter demonstration.
