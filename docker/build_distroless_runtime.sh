#!/usr/bin/env bash
set -euo pipefail

#
# Build-time script for producing a minimal runtime bundle suitable for
# `gcr.io/distroless/base-debian12:nonroot-arm64`.
#
# This script is executed in the Debian-based build stage and prepares:
# - `/opt/python`: Python dependencies installed via `pip --target`
# - `/usr/local/bin/gunicorn`: a wrapper so `uhd server run-production` works
# - `/opt/runtime-libs`: runtime binaries + shared libraries copied into distroless
#

readonly RUNTIME_LIBS_DIR="/opt/runtime-libs"

copy_binary_and_deps() {
  local binary_path="$1"

  # Copy the executable into the runtime bundle preserving its absolute path.
  mkdir -p "${RUNTIME_LIBS_DIR}"
  cp -v --parents "${binary_path}" "${RUNTIME_LIBS_DIR}/"

  # `ldd` prints all shared objects required by the binary. We extract only the
  # absolute paths so we can copy the libraries into the distroless runtime.
  #
  # We include both:
  # - the symlink itself (e.g. libz.so.1)
  # - the symlink target (e.g. libz.so.1.2.13)
  #
  # This is critical because distroless images do not have a package manager and
  # will not contain these libraries unless we copy them explicitly.
  ldd "${binary_path}" \
    | awk '{ if ($2 == "=>" && $3 ~ /^\//) print $3; else if ($1 ~ /^\//) print $1; }' \
    | while read -r lib_path; do \
        if [ -L "${lib_path}" ]; then \
          echo "${lib_path}"; \
          link_target="$(readlink "${lib_path}" || true)"; \
          if [ -n "${link_target}" ]; then \
            case "${link_target}" in \
              /*) echo "${link_target}" ;; \
              *) echo "$(dirname "${lib_path}")/${link_target}" ;; \
            esac; \
          fi; \
        elif [ -f "${lib_path}" ]; then \
          echo "${lib_path}"; \
        fi; \
      done \
    | sort -u \
    | xargs -r -I '{}' cp -vP --parents '{}' "${RUNTIME_LIBS_DIR}/"
}

copy_python_extension_deps() {
  local python_major_minor
  python_major_minor="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

  # Collect shared library deps for all CPython stdlib extension modules and
  # for any compiled third-party extension modules installed under /opt/python.
  #
  # Why:
  # - `gcr.io/distroless/base-debian12` does not include the system libraries that
  #   Python extension modules depend on (zlib, libffi, OpenSSL, etc.).
  # - Many Python packages ship compiled wheels with `.so` files.
  # - If we don't copy their dependent `.so` libs, imports will fail at runtime.
  (
    find "/usr/local/lib/python${python_major_minor}/lib-dynload" -type f -name '*.so' -print
    find /opt/python -type f -name '*.so' -print
  ) | while read -r so_path; do
        # Some `.so` files may cause `ldd` warnings; we ignore those and continue
        # so a single noisy dependency doesn't break the whole build.
        ldd "${so_path}" || true
      done \
    | awk '{ if ($2 == "=>" && $3 ~ /^\//) print $3; else if ($1 ~ /^\//) print $1; }' \
    | while read -r lib_path; do \
        case "${lib_path}" in \
          *"/../"*) \
            # Some wheel vendors reference libraries using paths containing `../`.
            # We normalise those so the copy step always targets a real file.
            resolved_path="$(readlink -f "${lib_path}" || true)"; \
            if [ -f "${resolved_path}" ]; then echo "${resolved_path}"; fi; \
            ;; \
          *) \
            if [ -L "${lib_path}" ]; then \
              echo "${lib_path}"; \
              link_target="$(readlink "${lib_path}" || true)"; \
              if [ -n "${link_target}" ]; then \
                case "${link_target}" in \
                  /*) echo "${link_target}" ;; \
                  *) echo "$(dirname "${lib_path}")/${link_target}" ;; \
                esac; \
              fi; \
            elif [ -f "${lib_path}" ]; then \
              echo "${lib_path}"; \
            fi; \
            ;; \
        esac; \
      done \
    | sort -u \
    | xargs -r -I '{}' cp -vP --parents '{}' "${RUNTIME_LIBS_DIR}/"
}

main() {
  apt-get update
  # Install build tools and headers needed for compiled wheels (e.g. psycopg2),
  # plus `bash` so we can copy it into the runtime.
  apt-get -y install --no-install-recommends bash gcc libpq-dev python3-dev libc-bin

  python -m pip install --upgrade pip
  # Install dependencies into a relocatable directory which is copied into the
  # distroless runtime image.
  python -m pip install --no-cache-dir --target /opt/python -r requirements-prod.txt

  # Provide a `gunicorn` executable for `uhd server run-production`.
  # `pip --target` installs packages but does not create console scripts.
  printf '%s\n' \
    '#!/usr/local/bin/python' \
    'import os' \
    'import sys' \
    '' \
    'os.execv(sys.executable, [sys.executable, "-m", "gunicorn", *sys.argv[1:]])' \
    > /usr/local/bin/gunicorn
  chmod 0755 /usr/local/bin/gunicorn

  # Ensure the compiled psycopg2 extension exists (required for Postgres).
  python -c "import glob, sys; matches=glob.glob('/opt/python/psycopg2/_psycopg*.so'); print(matches[0] if matches else ''); sys.exit(0 if matches else 1)"

  mkdir -p "${RUNTIME_LIBS_DIR}"

  # Copy bash into the runtime bundle so it is available in distroless.
  copy_binary_and_deps "/bin/bash"

  # Copy minimal coreutils needed by `uhd.sh` (e.g. `dirname`) into distroless.
  copy_binary_and_deps "/usr/bin/dirname"

  # Copy shared library deps required by Python's extension modules and installed wheels.
  copy_python_extension_deps

  # Remove build-only packages to keep the build stage lean.
  apt-get purge -y --auto-remove gcc libpq-dev python3-dev
  rm -rf /var/lib/apt/lists/* /var/cache/apt/*
}

main "$@"
