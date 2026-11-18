#!/usr/bin/env bash
set -Eeuo pipefail

#
# Build-time script for collecting shared library dependencies needed by the
# distroless runtime image. This script copies the python and system dirs needed
# for the prod build to work.

readonly DEPS_DIR="/deps"

copy_shared_libs() {
  local root="${1}"

  find "${root}" \( -type f -o -type l \) -name '*.so*' -print0 \
    | while IFS= read -r -d '' lib; do
        cp -vP --parents "${lib}" "${DEPS_DIR}/"
      done
}

copy_system_libs() {
  # Debian's merged-/usr layout means /lib is often a symlink to /usr/lib.
  # Resolve each libdir first so we don't end up copying a directory tree onto a
  # symlink when the final runtime image is assembled.
  local -A seen=()
  local libdir resolved

  for libdir in /lib/*-linux-gnu /usr/lib/*-linux-gnu; do
    [[ -d "${libdir}" ]] || continue

    resolved="$(readlink -f "${libdir}")"
    [[ -n "${seen[${resolved}]:-}" ]] && continue
    seen["${resolved}"]=1

    copy_shared_libs "${resolved}"
  done
}

main() {
  mkdir -p "${DEPS_DIR}"

  # Python installation includes shared objects under /usr/local.
  copy_shared_libs "/usr/local"

  # Architecture-specific system libraries.
  copy_system_libs
}

main "$@"
