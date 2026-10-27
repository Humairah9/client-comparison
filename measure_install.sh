#!/usr/bin/env bash
# Installs each library alone in a fresh virtualenv and reports what came with it.
# Usage: bash measure_install.sh > evidence/install.txt
for pkg in requests httpx httpx2; do
  dir=$(mktemp -d); python3 -m venv "$dir/v"
  "$dir/v/bin/pip" install -q --disable-pip-version-check "$pkg"
  echo "== $pkg"
  "$dir/v/bin/pip" list --disable-pip-version-check --format=freeze | grep -vi '^pip=='
  sp=$("$dir/v/bin/python" -c "import site;print(site.getsitepackages()[0])")
  total=$(du -sk "$sp" | cut -f1)
  pip_kb=$(du -sk "$sp"/pip* "$sp"/_distutils_hack "$sp"/distutils-precedence.pth 2>/dev/null | awk '{s+=$1} END{print s}')
  echo "library + dependencies on disk: $((total - pip_kb)) KB"
  echo
  rm -rf "$dir"
done
