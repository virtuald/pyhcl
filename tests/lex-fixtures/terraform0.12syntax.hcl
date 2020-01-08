locals {
  https_inbound_sg_id  = coalesce(join("", aws_security_group.https_inbound_sg.*.id), join("", data.aws_security_group.https_inbound_sg.*.id))
}

variable "env_variables" {
  type        = map(string)
  default     = { terraform: "needs dynamic blocks of code"}
}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  count      = var.module_count
  role       = aws_iam_role.role[count.index].name
}

resource "aws_rds_cluster" "interaction-database-cluster" {
  cluster_identifier      = local.rds_name

  scaling_configuration {
    max_capacity             = 256
    auto_pause               = var.environment == "prod" ? false : true
    seconds_until_auto_pause = var.environment == "prod" ? null : 3600
  }
}

resource "aws_lambda_function" "github_collector" {
  function_name    = var.github_collector_function_name

  environment {
    variables = {
      PROXY_AUTH    = join(":", [var.proxy_username, var.proxy_password])
    }
  }
}
