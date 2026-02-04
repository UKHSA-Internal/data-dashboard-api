#!/usr/bin/env bash
set -eu

#
# Build-time script for producing a minimal runtime bundle suitable for
# gcr.io/distroless/cc-debian12:nonroot.
#
# Prepares:
# - Python deps in /usr/local (default site-packages)
# - /deps: all shared libraries (*.so* files AND symlinks) from Python and system lib dirs
#

readonly DEPS_DIR="/deps"

main() {
  apt-get update
  apt-get -y install --no-install-recommends \
    bash zsh coreutils libc-bin libcap2 libtinfo6 gcc libpq-dev python3-dev
  rm -rf /var/lib/apt/lists/* /var/cache/apt/*

  python -m pip install --upgrade pip
  python -m pip install --no-cache-dir -r requirements-prod.txt

  # Kaleido ships a bash wrapper script at executable/kaleido that sets up
  # LD_LIBRARY_PATH and runs bin/kaleido. We keep it and ensure bash is available.

  mkdir -p "${DEPS_DIR}"

  # Copy all shared objects (files AND symlinks) from the Python installation.
  find /usr/local \( -type f -o -type l \) -name '*.so*' -print \
    | xargs -r -I '{}' cp -vP --parents '{}' "${DEPS_DIR}/"

  # Copy all shared objects (files AND symlinks) from architecture-specific system lib dirs.
  for libdir in /lib/*-linux-gnu /usr/lib/*-linux-gnu; do
    [ -d "${libdir}" ] || continue
    find "${libdir}" \( -type f -o -type l \) -name '*.so*' -print \
      | xargs -r -I '{}' cp -vP --parents '{}' "${DEPS_DIR}/"
  done

  apt-get update
  apt-get purge -y --auto-remove gcc libpq-dev python3-dev
  rm -rf /var/lib/apt/lists/* /var/cache/apt/*
}

main "$@"
