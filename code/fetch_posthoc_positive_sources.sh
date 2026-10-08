#!/usr/bin/env bash
set -euo pipefail
out="${1:-posthoc_positive_sources}"
mkdir -p "$out"
curl -L --fail --retry 3 'https://digitallibrary.un.org/record/4038545/files/S_2024_173-EN.pdf' -o "$out/S_2024_173-EN.pdf"
curl -L --fail --retry 3 'https://documents.un.org/api/symbol/access?l=en&s=A%2F78%2FPV.59&t=pdf' -o "$out/A_78_PV.59-EN.pdf"
shasum -a 256 "$out/S_2024_173-EN.pdf" "$out/A_78_PV.59-EN.pdf" | tee "$out/SHA256_POSTHOC_POSITIVES.txt"
