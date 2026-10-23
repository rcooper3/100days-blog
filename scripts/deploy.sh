#!/bin/bash
# Create or update the AWS infrastructure (S3 bucket + CloudFront), then
# publish the site. Only needed the first time or after changing
# infra/template.yaml — for daily posts use ./scripts/publish.sh.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

REGION=${AWS_REGION:-ap-southeast-2}
STACK_NAME=${STACK_NAME:-cyberako-100days-blog}
CERTIFICATE_ARN=${CERTIFICATE_ARN:?"Set CERTIFICATE_ARN to the ACM cert ARN in us-east-1 (run ./scripts/request-cert.sh)"}
DOMAIN_NAME=${DOMAIN_NAME:-100days.cyberako.blog}

echo "==> Deploying stack: $STACK_NAME to $REGION"
aws cloudformation deploy \
  --template-file "$PROJECT_ROOT/infra/template.yaml" \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --no-fail-on-empty-changeset \
  --parameter-overrides "CertificateArn=$CERTIFICATE_ARN" "DomainName=$DOMAIN_NAME"

CUSTOM_CNAME=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='CustomDomainCname'].OutputValue" --output text)

"$SCRIPT_DIR/publish.sh"

echo ""
echo "If not done already, add this CNAME in WordPress.com (Domains > cyberako.blog > DNS records):"
echo "  Type:  CNAME"
echo "  Name:  ${DOMAIN_NAME%%.*}"
echo "  Value: $CUSTOM_CNAME"
