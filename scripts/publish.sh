#!/bin/bash
# Daily publish: freeze the Flask app to build/, upload it to S3, and clear
# the CloudFront cache so the new post shows up straight away.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

REGION=${AWS_REGION:-ap-southeast-2}
STACK_NAME=${STACK_NAME:-cyberako-100days-blog}
PYTHON="$PROJECT_ROOT/.venv/bin/python"

echo "==> Freezing site"
cd "$PROJECT_ROOT"
"$PYTHON" freeze.py

OUTPUTS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" \
  --query "Stacks[0].Outputs" --output json)
BUCKET=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="SiteBucket") | .OutputValue')
DIST_ID=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="DistributionId") | .OutputValue')

echo "==> Syncing build/ to s3://$BUCKET"
aws s3 sync "$PROJECT_ROOT/build/" "s3://$BUCKET/" \
  --delete \
  --cache-control "max-age=300" \
  --only-show-errors

echo "==> Invalidating CloudFront cache"
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*" > /dev/null

echo ""
echo "Published: https://${DOMAIN_NAME:-100days.cyberako.blog}"
