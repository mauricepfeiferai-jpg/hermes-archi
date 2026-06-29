#!/bin/zsh
FILE="${1}"
if [ -z "$FILE" ]; then
  echo "Usage: driver.sh path/to/output.md"
  exit 1
fi
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DATE=$(date +%Y-%m-%d)
{
  echo "# Review: $FILE"
  echo ""
  echo "Date: $DATE"
  echo "Status: STUB REVIEW"
  echo ""
  echo "## Checks"
  echo "- [ ] Quality gates met"
  echo "- [ ] No secrets/PII/legal risk"
  echo "- [ ] Tone matches brand"
  echo "- [ ] CTA clear and safe"
  echo ""
  echo "## Recommendation"
  echo "APPROVE (subject to human final say)"
} > "$ROOT/loop/outputs/review_$(basename "$FILE")"
echo "Review stub written"
