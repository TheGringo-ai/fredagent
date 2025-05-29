#!/bin/bash

BASE_URL="http://localhost:8000"

echo -e "\n▶ /health"
curl -s "$BASE_URL/health" | jq

echo -e "\n▶ /dev/plan"
curl -s -X POST "$BASE_URL/dev/plan" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Build a web dashboard with AI assistant features"}' | jq

echo -e "\n▶ /dev/plan/diagnose"
curl -s -X POST "$BASE_URL/dev/plan/diagnose" \
  -H "Content-Type: application/json" \
  -d '{"plan": ["Step 1", "Step 2"]}' | jq

echo -e "\n▶ /dev/plan/auto"
curl -s -X POST "$BASE_URL/dev/plan/auto" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Automate app scaffolding"}' | jq

echo -e "\n▶ /agent/auto_fix"
curl -s -X POST "$BASE_URL/agent/auto_fix" \
  -H "Content-Type: application/json" \
  -d '{"code": "import os\\nprint(os.listdir())"}' | jq

echo -e "\n▶ /dev/patch"
curl -s -X POST "$BASE_URL/dev/patch" \
  -H "Content-Type: application/json" \
  -d '{"plan": ["Step 1", "Step 2"]}' | jq

echo -e "\n✅ Done running backend route tests."
