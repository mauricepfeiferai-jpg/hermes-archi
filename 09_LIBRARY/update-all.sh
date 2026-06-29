#!/bin/zsh
# Update all cloned repositories in 09_LIBRARY
for d in 09_LIBRARY/*/; do
  if [ -d "$d/.git" ]; then
    echo "Updating $d..."
    (cd "$d" && git pull --depth 1)
  fi
done
