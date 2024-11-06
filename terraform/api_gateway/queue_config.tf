# FIFO SQS Queue
resource "aws_sqs_queue" "fifo_queue" {
 name                      = "immunisation-ack-metadata-queue.fifo"# Must end with .fifo
 fifo_queue                = true
 content_based_deduplication = true # Optional, helps with deduplication
 visibility_timeout_seconds = 60
}

