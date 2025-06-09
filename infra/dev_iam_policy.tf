# IAM policy for Osouji Reminder v2 developer access
resource "aws_iam_policy" "osouji_reminder_dev" {
  name        = "osouji-reminder-v2-developer"
  description = "Permissions for developers to manage Osouji Reminder v2 infrastructure via Terraform."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # S3 state bucket access
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::osouji-reminder-v2-tf-state",
          "arn:aws:s3:::osouji-reminder-v2-tf-state/*"
        ]
      },
      # Lambda management
      {
        Effect   = "Allow"
        Action   = "lambda:*"
        Resource = "*"
      },
      # IAM role and policy management (for Lambda and Scheduler roles)
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole",
          "iam:GetRole",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:PutRolePolicy",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies"
        ]
        Resource = [
          "arn:aws:iam::*:role/iam_for_lambda",
          "arn:aws:iam::*:role/iam_for_scheduler"
        ]
      },
      # EventBridge Scheduler
      {
        Effect = "Allow"
        Action = [
          "events:*",
          "scheduler:*"
        ]
        Resource = "*"
      },
      # Secrets Manager (read-only)
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecrets"
        ]
        Resource = "*"
      },
      # CloudWatch Logs (for Lambda debugging)
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups"
        ]
        Resource = "*"
      }
    ]
  })
}
