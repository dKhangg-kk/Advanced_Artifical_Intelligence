#!/usr/bin/env sh
# Ghep bao cao. Co pandoc: ban day du (hinh, cong thuc, muc luc) -> .docx va PDF (can LibreOffice).
# Khong co pandoc: ban nhanh bang python-docx (khong co hinh), chi .docx.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
PYTHON=${PYTHON:-python}

cd "$PROJECT_ROOT"
if command -v pandoc >/dev/null 2>&1; then
  if command -v soffice >/dev/null 2>&1 || command -v libreoffice >/dev/null 2>&1; then
    exec "$PYTHON" docs/report/build_docx_pdf.py "$@"
  fi
  exec "$PYTHON" docs/report/build_docx_pdf.py --no-pdf "$@"
fi
exec "$PYTHON" docs/report/build_report.py
