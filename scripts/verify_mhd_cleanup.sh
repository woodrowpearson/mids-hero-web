#!/bin/bash
set -e

echo "🔍 Searching for MHD references..."

# Search code for MHD/I12 references
rg -i "mhd|i12|midsreborn" \
  --type py \
  --type ts \
  --glob "*.tsx" \
  --glob "!archive/**" \
  --glob "!*.md" \
  --glob "!docs/**" \
  > /tmp/mhd_refs.txt || true

if [ -s /tmp/mhd_refs.txt ]; then
  echo "❌ Found MHD references in code:"
  cat /tmp/mhd_refs.txt
  exit 1
else
  echo "✅ No MHD references found in code"
fi

# Verify deleted directories
if [ -d "backend/app/mhd_parser" ]; then
  echo "❌ MHD parser directory still exists"
  exit 1
fi

if [ -d "backend/backend/app/core" ]; then
  echo "❌ Nested backend core directory still exists"
  exit 1
fi

echo "✅ All deleted directories confirmed removed"

# Verify archive structure
if [ ! -d "archive/mhd-parser" ]; then
  echo "❌ MHD parser not found in archive"
  exit 1
fi

echo "✅ Archive structure correct"

echo ""
echo "🎉 Cleanup verification passed!"
