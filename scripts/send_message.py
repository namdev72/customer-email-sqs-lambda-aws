"""
send_message.py
---------------
Sends a test order-confirmation message to the Amazon SQS queue so you can
validate the full pipeline:

    This script  →  Amazon SQS  →  AWS Lambda  →  Amazon SES  →  Customer Email

Usage
-----
    python scripts/send_message.py

Prerequisites
-------------
  * AWS CLI configured  (aws configure)
  * The Terraform infrastructure already deployed  (terraform apply)
  * The sender email verified in Amazon SES

Environment variables (optional overrides)
------------------------------------------
  SQS_QUEUE_URL   – full URL of the SQS queue
                    (defaults to reading terraform output automatically)
  AWS_REGION      – AWS region (default: ap-south-1)
"""

import json
import os
import subprocess
import boto3

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

# Try to get the queue URL from an env variable; fall back to terraform output.
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "")


def get_queue_url_from_terraform() -> str:
    """Read the queue URL from `terraform output` when env var is not set."""
    terraform_dir = os.path.join(
        os.path.dirname(__file__), "..", "terraform"
    )
    try:
        result = subprocess.run(
            ["terraform", "output", "-raw", "queue_url"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()
        if url:
            return url
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"[WARN] Could not read terraform output: {exc}")
    return ""


# ---------------------------------------------------------------------------
# Sample order payload  –  edit these fields before running
# ---------------------------------------------------------------------------

ORDER_MESSAGE = {
    "customer_name": "Souvik De",
    "email": "techsj04@gmail.com",   # Must be a SES-verified address in sandbox
    "order_id": "ORD-1001",
    "amount": "999",
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def send_order_to_sqs(queue_url: str, order: dict) -> None:
    """Send a single order message to the SQS queue."""

    sqs = boto3.client("sqs", region_name=AWS_REGION)

    message_body = json.dumps(order)

    print("=" * 60)
    print("Sending order message to SQS …")
    print(f"  Queue URL : {queue_url}")
    print(f"  Payload   : {message_body}")
    print("=" * 60)

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
    )

    message_id = response.get("MessageId", "N/A")
    http_status = response["ResponseMetadata"]["HTTPStatusCode"]

    print(f"\n✅ Message sent successfully!")
    print(f"   MessageId  : {message_id}")
    print(f"   HTTP Status: {http_status}")
    print("\nWhat happens next:")
    print("  1. SQS queues the message")
    print("  2. Lambda is triggered automatically (event source mapping)")
    print("  3. Lambda reads the message and calls Amazon SES")
    print(f"  4. SES sends the order confirmation email to: {order['email']}")
    print("  5. Lambda logs are written to CloudWatch")


def main() -> None:
    global SQS_QUEUE_URL

    if not SQS_QUEUE_URL:
        print("[INFO] SQS_QUEUE_URL not set – reading from Terraform output …")
        SQS_QUEUE_URL = get_queue_url_from_terraform()

    if not SQS_QUEUE_URL:
        print(
            "\n[ERROR] Could not determine the SQS queue URL.\n"
            "Please either:\n"
            "  a) Set the environment variable:  SQS_QUEUE_URL=<url>\n"
            "  b) Run  terraform apply  in the terraform/ directory first.\n"
        )
        raise SystemExit(1)

    send_order_to_sqs(SQS_QUEUE_URL, ORDER_MESSAGE)


if __name__ == "__main__":
    main()
