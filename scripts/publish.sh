#!/bin/bash
# Daily publish: freeze the Flask app to build/, upload it to S3, clear
# the CloudFront cache so the new post shows up straight away, then commit
# and push to GitHub as a backup.
#
#   ./scripts/publish.sh                    # commit message: "Day N: <title>"
#   ./scripts/publish.sh "Fix typo in day 3"  # custom commit message
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

echo "Published: https://${DOMAIN_NAME:-100days.cyberako.blog}"

echo "==> Backing up to GitHub"
git add -A
if git diff --cached --quiet; then
  echo "Nothing new to commit"
else
  # Default message names the latest published post, e.g. "Day 4: Collections module".
  MESSAGE=${1:-$("$PYTHON" -c "from posts import load_posts; p = load_posts()[0]; print(f'Day {p.day}: {p.title}')")}
  git commit -q -m "$MESSAGE"
  echo "Committed: $MESSAGE"
fi
# The site is already live at this point, so a failed push is a warning, not an error.
if git push -q; then
  echo "Pushed to $(git remote get-url origin)"
else
  echo "WARNING: git push failed. The site is published; run 'git push' once fixed."
fi
