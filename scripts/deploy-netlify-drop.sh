#!/bin/zsh
# Deploy AI Empire products to Netlify Drop (manual or CLI)
# Usage:
#   Manual: open https://app.netlify.com/drop and drag /tmp/ai-empire-products-drop.zip
#   CLI:    NETLIFY_AUTH_TOKEN=xxx bash scripts/deploy-netlify-drop.sh

DROP_ZIP="/tmp/ai-empire-products-drop.zip"

echo "AI Empire — Netlify Drop Deploy"
echo "================================"
echo "Drop zip: $DROP_ZIP"

if [ -z "$NETLIFY_AUTH_TOKEN" ]; then
  echo ""
  echo "NETLIFY_AUTH_TOKEN not set."
  echo "Fastest path: open https://app.netlify.com/drop and drag the zip."
  echo "For CLI auto-deploy: get a token at https://app.netlify.com/user/applications#personal-access-tokens"
  exit 0
fi

if ! command -v npx &> /dev/null; then
  echo "npx not found. Install Node.js first."
  exit 1
fi

npx netlify deploy --prod --dir=/tmp/ai-empire-drop-site --auth "$NETLIFY_AUTH_TOKEN" --site=ai-empire-products
