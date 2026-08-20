# CampusHire Analytics + Power BI

## In the CampusHire app
1. Log in as a candidate.
2. Open **Analytics** in the top navigation.
3. The dashboard shows:
   - Total applications
   - Shortlisted applications
   - Interviews
   - Average ATS score
   - Applied / Shortlisted / Interview / Selected / Rejected distribution
4. Click **Export for Power BI** to download `campushire_candidate_analytics.csv`.

## In Power BI Desktop
1. Open Power BI Desktop.
2. Select **Get Data → Text/CSV**.
3. Choose `campushire_candidate_analytics.csv`.
4. Load the table.
5. For the pie/doughnut chart, use:
   - Legend: `Status`
   - Values: `Job` (Count)
6. Add cards for application count and average ATS score if desired.

The Django dashboard remains available even when Power BI Desktop is not installed, while the CSV export keeps the same application-status data ready for Power BI.
