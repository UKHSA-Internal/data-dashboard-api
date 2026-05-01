#!/usr/bin/env bash
set -eu

#
# Build-time script for collecting shared library dependencies needed by the
# distroless runtime image.
#
# Produces:
# - /deps: all shared libraries (*.so* files AND symlinks) from Python and system
#   library directories, preserving parent paths.
#

readonly DEPS_DIR="/deps"

main() {
  mkdir -p "${DEPS_DIR}"

  # Copy all shared objects (files AND symlinks) from the Python installation.
  find /usr/local \( -type f -o -type l \) -name '*.so*' -print \
    | xargs -r -I '{}' cp -vP --parents '{}' "${DEPS_DIR}/"

  # Copy all shared objects (files AND symlinks) from architecture-specific system lib dirs.
  for libdir in /lib/*-linux-gnu /usr/lib/*-linux-gnu; do
    [[ -d "${libdir}" ]] || continue
    find "${libdir}" \( -type f -o -type l \) -name '*.so*' -print \
      | xargs -r -I '{}' cp -vP --parents '{}' "${DEPS_DIR}/"
  done

  return 0
}

main "$@"
