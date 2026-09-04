#!/bin/bash
set -Eeuo pipefail
umask 027

readonly ACCOUNT_HOME='/home/v0398ees6dry'
readonly REPOSITORY_ROOT='/home/v0398ees6dry/repositories/stronger-at-home-staging'
readonly DOCUMENT_ROOT='/home/v0398ees6dry/public_html/staging.stronger-at-home.co.uk'
readonly CONFIG_PATH='/home/v0398ees6dry/private/stronger-at-home/staging/site.php'
readonly RELEASE_ROOT='/home/v0398ees6dry/stronger-at-home-releases/staging'
readonly SOURCE_SHA='cb55e7ff184bb8fd2d4355fd3544aaf314a8bf2f'
readonly RELEASE_DIRECTORY="$RELEASE_ROOT/$SOURCE_SHA"
readonly NEXT_DIRECTORY="$DOCUMENT_ROOT.next-$SOURCE_SHA"
readonly PREVIOUS_DIRECTORY="$RELEASE_DIRECTORY/previous-public"

fail() {
  printf '%s
' "$1" >&2
  exit 1
}

[[ "${HOME:-}" == "$ACCOUNT_HOME" ]] || fail 'Unexpected cPanel account home.'
[[ "$(pwd -P)" == "$REPOSITORY_ROOT" ]] || fail 'Unexpected cPanel repository root.'
[[ -d public && ! -L public && -f public/.htaccess && ! -L public/.htaccess ]] || fail 'Missing public release tree.'
[[ -d public/api/src && ! -L public/api/src ]] || fail 'Missing application source tree.'
[[ -d vendor && ! -L vendor && -f vendor/autoload.php && ! -L vendor/autoload.php ]] || fail 'Missing vendor release tree.'
[[ -f "$CONFIG_PATH" && ! -L "$CONFIG_PATH" ]] || fail 'Missing external environment configuration.'
[[ ! -e "$RELEASE_DIRECTORY" && ! -L "$RELEASE_DIRECTORY" ]] || fail 'Release directory already exists.'
[[ ! -e "$NEXT_DIRECTORY" && ! -L "$NEXT_DIRECTORY" ]] || fail 'Next document-root directory already exists.'

mkdir -p -- "$RELEASE_ROOT"
mkdir -- "$RELEASE_DIRECTORY"
cp -a -- vendor "$RELEASE_DIRECTORY/vendor"
mkdir -p -- "$RELEASE_DIRECTORY/site/api"
cp -a -- public/api/src "$RELEASE_DIRECTORY/site/api/src"
cp -a -- public "$NEXT_DIRECTORY"

swap_pending=0
restore_previous() {
  local status=$?
  if [[ "$swap_pending" -eq 1 && ! -e "$DOCUMENT_ROOT" && -d "$PREVIOUS_DIRECTORY" ]]; then
    mv -- "$PREVIOUS_DIRECTORY" "$DOCUMENT_ROOT" || true
  fi
  exit "$status"
}
trap restore_previous EXIT

swap_pending=1
mv -- "$DOCUMENT_ROOT" "$PREVIOUS_DIRECTORY"
mv -- "$NEXT_DIRECTORY" "$DOCUMENT_ROOT"
swap_pending=0
printf '%s
' "$SOURCE_SHA" > "$RELEASE_DIRECTORY/deployed-source-sha"
trap - EXIT
