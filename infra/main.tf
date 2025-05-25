# Policy document for lambda
data "aws_iam_policy_document" "assume_role_lambda" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Policy document for event bridge scheduler
data "aws_iam_policy_document" "assume_role_scheduler" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Policy document for scheduler to invoke lambda
data "aws_iam_policy_document" "scheduler_invoke_lambda" {
  statement {
    effect = "Allow"
    actions = [
      "lambda:InvokeFunction",
    ]
    resources = [aws_lambda_function.notify_trash_lambda.arn]
  }
}

# Roles
resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}

resource "aws_iam_role" "iam_for_scheduler" {
  name               = "iam_for_scheduler"
  assume_role_policy = data.aws_iam_policy_document.assume_role_scheduler.json
}

# Policies
resource "aws_iam_policy" "scheduler_invoke_lambda_policy" {
  name        = "scheduler-invoke-lambda-policy"
  description = "Policy for Scheduler to invoke Lambda"
  policy      = data.aws_iam_policy_document.scheduler_invoke_lambda.json
}

# Attach policy to scheduler role
resource "aws_iam_role_policy_attachment" "scheduler_invoke_lambda_attach" {
  role       = aws_iam_role.iam_for_scheduler.name
  policy_arn = aws_iam_policy.scheduler_invoke_lambda_policy.arn
}


# Lambda function
data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/notify_trash_lambda.py"
  output_path = "notify_trash_lambda_function_src.zip"
}

data "aws_secretsmanager_secret_version" "line_access_token" {
  secret_id = "osouji-v2/line_channel_access_token"
}

data "aws_secretsmanager_secret_version" "recipient_id" {
  secret_id = "osouji-v2/recipient_id"
}

resource "aws_lambda_function" "notify_trash_lambda" {
  filename      = "notify_trash_lambda_function_src.zip"
  function_name = "notify_trash_lambda"
  role          = aws_iam_role.iam_for_lambda.arn

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.10"
  handler = "notify_trash_lambda.lambda_handler"

  environment {
    variables = {
      LINE_CHANNEL_ACCESS_TOKEN = data.aws_secretsmanager_secret_version.line_access_token.secret_string
      RECIPIENT_ID              = data.aws_secretsmanager_secret_version.recipient_id.secret_string
    }
  }

  layers = ["arn:aws:lambda:ap-northeast-1:770693421928:layer:Klayers-p310-requests:18"]
}

# Allow scheduler to invoke lambda
resource "aws_lambda_permission" "allow_scheduler_invoke" {
  statement_id  = "AllowExecutionFromScheduler"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notify_trash_lambda.function_name
  principal     = "scheduler.amazonaws.com"
  source_arn    = aws_scheduler_schedule.trash_notification_schedule.arn
}

# Scheduler
resource "aws_scheduler_schedule" "trash_notification_schedule" {
  name       = "trash_notification_schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  # Sun to Thu every night 9:00 PM Japan time
  schedule_expression = "cron(00 12 ? * 1-5 *)"

  target {
    arn      = aws_lambda_function.notify_trash_lambda.arn
    role_arn = aws_iam_role.iam_for_scheduler.arn

    input = jsonencode({
      identifier = "trash_notification"
    })
  }

}

resource "aws_scheduler_schedule" "cleaning_duty_schedule" {
  name       = "cleaning_duty_schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  # Sun to Thu every night 9:00 PM Japan time
  schedule_expression = "cron(00 12 ? * 1 *)"

  target {
    arn      = aws_lambda_function.notify_trash_lambda.arn
    role_arn = aws_iam_role.iam_for_scheduler.arn
    input = jsonencode({
      identifier = "cleaning_duty_schedule"
    })
  }
}

resource "aws_scheduler_schedule" "rent_payment_notification_schedule" {
  name       = "rent_payment_notification_schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }


  # Every month on 24th
  schedule_expression = "cron(00 3 24 * ? *)"

  target {
    arn      = aws_lambda_function.notify_trash_lambda.arn
    role_arn = aws_iam_role.iam_for_scheduler.arn
    input = jsonencode({
      identifier = "rent_payment_notification"
    })
  }
}

# logs

data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}


resource "aws_iam_policy" "lambda_logging" {
  name        = "lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}
