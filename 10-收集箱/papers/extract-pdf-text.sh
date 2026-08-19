#!/usr/bin/env bash
# 从 PDF 提取可翻译的 .txt 旁路（Comment Translate 不支持 PDF 预览内直接翻译）
set -euo pipefail
pdf="${1:?用法: extract-pdf-text.sh <file.pdf>}"
out="${pdf%.pdf}.txt"
pdftotext -layout "$pdf" "$out"
echo "已生成: $out"
