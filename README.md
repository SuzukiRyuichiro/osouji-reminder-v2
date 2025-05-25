# Osouji Reminder v2

A fully automated notification system for a share house, built with AWS Lambda (Python) and Terraform. It periodically notifies a LINE group chat about:

- What trash to take out on a given day
- Who is responsible for cleaning duties each week
- Monthly rent payment reminders

## Architecture

- **AWS Lambda**: Python function (`notify_trash_lambda.py`) sends messages to LINE via the Messaging API.
- **AWS EventBridge Scheduler**: Triggers the Lambda on a schedule (trash, cleaning, rent reminders) using cron expressions.
- **Terraform**: All infrastructure is defined as code in `infra/` and deployed via Terraform. State is stored in S3.

## How it Works

1. **Scheduling**: AWS Scheduler triggers the Lambda at configured times (e.g., weekday mornings for trash, weekly for cleaning, monthly for rent).
2. **Notification Logic**: The Lambda determines the correct message (trash type, cleaning rotation, rent reminder) and sends it to the LINE group using the Messaging API.
3. **Configuration**: User IDs and tokens are injected as environment variables from AWS Secrets Manager and Terraform variables.

## Deployment

1. **Install Terraform** and configure your AWS credentials/profile.
2. **Set up secrets** in AWS Secrets Manager for LINE access token and recipient/user IDs.
3. **Edit `infra/variables.tf`** to populate the house member's LINE IDs.
4. **Run Terraform**:
   ```sh
   cd infra
   terraform init
   terraform apply
   ```
   This will build and deploy all resources, package the Lambda, and set up schedules.

## Development

- Lambda code: `notify_trash_lambda.py`
- Infrastructure: `infra/` (Terraform)

## Notes

- The backend Terraform state is stored in an S3 bucket.
- All secrets are managed outside of source control.
- The system is timezone-aware for Japan (JST).

---
