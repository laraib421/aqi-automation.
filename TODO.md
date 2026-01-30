# AQI Automation Pipeline Fix TODO

## Steps to Complete
- [x] Diagnose pipeline failure: Identified missing environment variables in GitHub Actions
- [x] Update .github/workflows/pipeline.yml to include env variables from secrets
- [ ] Ensure GitHub repository secrets are configured for MONGO_URI and OPENWEATHER_API_KEY
- [ ] Test the pipeline by triggering a manual run or waiting for the next scheduled run
- [ ] Verify that the pipeline completes successfully without errors
