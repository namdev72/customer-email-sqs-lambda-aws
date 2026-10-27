# ------------------------------------------------------------------------------
# Amazon SES – Email Identity Verification
#
# SES must verify the sender address before it can send emails.
# In sandbox mode, both sender AND recipient addresses must be verified.
# To move out of sandbox, request production access from the AWS console.
# ------------------------------------------------------------------------------

resource "aws_ses_email_identity" "sender" {

  email = var.sender_email

}
