#!/bin/bash
# Tear down the blog's AWS resources. Your posts in content/ are untouched.
set -e

REGION=${AWS_REGION:-ap-southeast-2}
STACK_NAME=${STACK_NAME:-cyberako-100days-blog}
DOMAIN_NAME=${DOMAIN_NAME:-100days.cyberako.blog}

read -r -p "Delete stack $STACK_NAME (bucket + CloudFront)? [y/N] " answer
[ "$answer" = "y" ] || exit 0

BUCKET=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='SiteBucket'].OutputValue" --output text)

# CloudFormation refuses to delete a non-empty bucket.
echo "==> Emptying s3://$BUCKET"
aws s3 rm "s3://$BUCKET" --recursive

echo "==> Deleting stack (CloudFront deletion takes several minutes)"
aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"
aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$REGION"

CERT_ARN=$(aws acm list-certificates --region us-east-1 \
  --query "CertificateSummaryList[?DomainName=='$DOMAIN_NAME'].CertificateArn | [0]" --output text)
if [ -n "$CERT_ARN" ] && [ "$CERT_ARN" != "None" ]; then
  read -r -p "Also delete the ACM certificate for $DOMAIN_NAME? (free to keep) [y/N] " answer
  if [ "$answer" = "y" ]; then
    aws acm delete-certificate --region us-east-1 --certificate-arn "$CERT_ARN"
  fi
fi

echo ""
echo "Done. Remove these manually in WordPress.com if you're finished for good:"
echo "  - the ${DOMAIN_NAME%%.*} CNAME"
echo "  - the ACM validation CNAME (_<hash>.${DOMAIN_NAME%%.*})"
