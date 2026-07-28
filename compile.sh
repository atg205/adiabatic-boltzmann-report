#!/usr/bin/env bash
# Kompilacja report.tex (pdflatex + bibtex + glossaries) przez latexmk.
# Użycie:
#   ./compile.sh          - kompiluje do build/ i kopiuje PDF do katalogu głównego
#   ./compile.sh watch    - kompiluje w pętli przy każdej zmianie plików
#   ./compile.sh clean    - usuwa pliki pomocnicze z build/
set -euo pipefail
cd "$(dirname "$0")"

MAIN=report

case "${1:-}" in
    clean)
        latexmk -C "$MAIN"
        ;;
    watch)
        latexmk -pvc -interaction=nonstopmode "$MAIN"
        ;;
    *)
        latexmk -interaction=nonstopmode -halt-on-error "$MAIN"
        cp "build/$MAIN.pdf" "$MAIN.pdf"
        echo "OK: $MAIN.pdf"
        ;;
esac
