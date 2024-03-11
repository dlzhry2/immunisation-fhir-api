resource "aws_cloudwatch_log_group" "batch_task_log_group" {
  name              = "${local.prefix}-task"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_stream" "container_log_stream" {
  name           = "${local.prefix}-task"
  log_group_name = aws_cloudwatch_log_group.batch_task_log_group.name

}
