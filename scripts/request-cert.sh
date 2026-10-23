#!/bin/bash
# One-off: request (or find) the ACM certificate for the blog's domain and
# print the DNS validation CNAME to add in WordPress.com.
# CloudFront only accepts certificates from us-east-1, whatever region the
# stack itself is in.
set -e

DOMAIN_NAME=${DOMAIN_NAME:-100days.cyberako.blog}
PARENT_DOMAIN=${PARENT_DOMAIN:-cyberako.blog}

CERT_ARN=$(aws acm list-certificates --region us-east-1 \
  --certificate-statuses ISSUED PENDING_VALIDATION \
  --query "CertificateSummaryList[?DomainName=='$DOMAIN_NAME'].CertificateArn | [0]" \
  --output text)

if [ -z "$CERT_ARN" ] || [ "$CERT_ARN" = "None" ]; then
  echo "==> Requesting certificate for $DOMAIN_NAME"
  CERT_ARN=$(aws acm request-certificate --region us-east-1 \
    --domain-name "$DOMAIN_NAME" \
    --validation-method DNS \
    --query CertificateArn --output text)
else
  echo "==> Found existing certificate for $DOMAIN_NAME"
fi

# The validation record takes a few seconds to appear on a new request.
for _ in $(seq 1 20); do
  CERT=$(aws acm describe-certificate --region us-east-1 --certificate-arn "$CERT_ARN" --output json)
  RECORD_NAME=$(echo "$CERT" | jq -r '.Certificate.DomainValidationOptions[0].ResourceRecord.Name // empty')
  [ -n "$RECORD_NAME" ] && break
  sleep 3
done

STATUS=$(echo "$CERT" | jq -r '.Certificate.Status')
RECORD_VALUE=$(echo "$CERT" | jq -r '.Certificate.DomainValidationOptions[0].ResourceRecord.Value')

# WordPress.com wants the host part only, without ".cyberako.blog." on the end.
HOST=${RECORD_NAME%.}
HOST=${HOST%.$PARENT_DOMAIN}

echo ""
echo "Certificate ARN: $CERT_ARN"
echo "Status:          $STATUS"
echo ""
if [ "$STATUS" = "ISSUED" ]; then
  echo "Certificate is issued. Deploy with:"
  echo "  CERTIFICATE_ARN=$CERT_ARN ./scripts/deploy.sh"
else
  echo "Add this CNAME in WordPress.com (Domains > $PARENT_DOMAIN > DNS records):"
  echo "  Type:  CNAME"
  echo "  Name:  $HOST"
  echo "  Value: ${RECORD_VALUE%.}"
  echo ""
  echo "Then re-run this script until Status shows ISSUED (usually 5-30 minutes)."
fi
