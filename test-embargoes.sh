#!/bin/bash
set -euo pipefail

DB_PATH="${DB_PATH:-db.sqlite3}"

if ! command -v sqlite3 >/dev/null 2>&1; then
    echo "ERROR: sqlite3 is required but not installed."
    exit 1
fi

if [[ ! -f "$DB_PATH" ]]; then
    echo "ERROR: database file not found: $DB_PATH"
    exit 1
fi

print_header() {
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

run_sql() {
    local sql="$1"
    echo "SQL>"
    echo "$sql"
    echo "RESULT>"
    sqlite3 -header -column "$DB_PATH" "$sql"
    echo
}

print_header "Embargo UI Test Plan Generator (Childhood Vaccinations)"
echo "Database: $DB_PATH"
echo "Generated at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo

COMPOSITE_PAGE_SQL="SELECT p.id
FROM wagtailcore_page p
JOIN composite_compositepage c ON c.page_ptr_id = p.id
WHERE lower(p.title) = lower('Childhood vaccinations')
ORDER BY p.id
LIMIT 1;"

TOPIC_PAGE_SQL="SELECT p.id
FROM wagtailcore_page p
JOIN topic_topicpage t ON t.page_ptr_id = p.id
WHERE lower(p.slug) = lower('childhood-vaccinations')
ORDER BY p.id
LIMIT 1;"

COMPOSITE_PAGE_ID="$(sqlite3 "$DB_PATH" "$COMPOSITE_PAGE_SQL")"
TOPIC_PAGE_ID="$(sqlite3 "$DB_PATH" "$TOPIC_PAGE_SQL")"

if [[ -z "$COMPOSITE_PAGE_ID" || -z "$TOPIC_PAGE_ID" ]]; then
    echo "ERROR: Could not resolve Childhood vaccinations page ids."
    echo "Check that CMS test content is loaded."
    echo
    run_sql "$COMPOSITE_PAGE_SQL"
    run_sql "$TOPIC_PAGE_SQL"
    exit 1
fi

print_header "Resolved CMS Pages"
run_sql "SELECT id, title, slug, live, has_unpublished_changes FROM wagtailcore_page WHERE id IN ($COMPOSITE_PAGE_ID, $TOPIC_PAGE_ID) ORDER BY id;"

BODY_SQL="SELECT body FROM topic_topicpage WHERE page_ptr_id = $TOPIC_PAGE_ID;"
BODY_EVIDENCE_SQL="SELECT page_ptr_id, length(body) AS body_length_chars FROM topic_topicpage WHERE page_ptr_id = $TOPIC_PAGE_ID;"

BODY_JSON="$(sqlite3 "$DB_PATH" "$BODY_SQL")"

if [[ -z "$BODY_JSON" ]]; then
    echo "ERROR: Topic page body is empty for page_ptr_id=$TOPIC_PAGE_ID"
    exit 1
fi

mapfile -t METRICS < <(
    printf '%s' "$BODY_JSON" \
        | grep -oE '"metric"[[:space:]]*:[[:space:]]*\{[^}]*"value"[[:space:]]*:[[:space:]]*"[^"]+"' \
        | sed -E 's/.*"value"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/' \
        | sort -u
)

if [[ ${#METRICS[@]} -eq 0 ]]; then
    echo "ERROR: No metrics were parsed from Childhood vaccinations topic body."
    echo "SQL used to fetch body:"
    echo "$BODY_SQL"
    exit 1
fi

METRIC_IN=""
for metric in "${METRICS[@]}"; do
    METRIC_IN+="'${metric}',"
done
METRIC_IN="${METRIC_IN%,}"

print_header "SQL Used To Determine Metrics In Scope"
run_sql "$BODY_EVIDENCE_SQL"
echo "SQL used for metric extraction:"
echo "$BODY_SQL"
echo

echo "Parsed metrics from page body:"
for metric in "${METRICS[@]}"; do
    echo "- $metric"
done
echo

FUTURE_EMBARGO_SQL="SELECT
    m.name AS metric_name,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN ts.embargo IS NULL THEN 1 ELSE 0 END) AS null_embargo_rows,
    SUM(CASE WHEN ts.embargo > datetime('now') THEN 1 ELSE 0 END) AS rows_under_embargo_now,
    MIN(ts.embargo) AS min_embargo,
    MAX(ts.embargo) AS max_embargo
FROM data_coretimeseries ts
JOIN data_metric m ON m.id = ts.metric_id
WHERE m.name IN ($METRIC_IN)
GROUP BY m.name
ORDER BY m.name;"

print_header "Current Embargo State For Childhood Vaccination Metrics"
run_sql "$FUTURE_EMBARGO_SQL"

X_TIME_SQL="SELECT COALESCE(
    datetime(MIN(CASE WHEN ts.embargo > datetime('now') THEN ts.embargo END), '-1 second'),
    datetime(MIN(ts.embargo), '-1 second')
) AS suggested_x_datetime_utc
FROM data_coretimeseries ts
JOIN data_metric m ON m.id = ts.metric_id
WHERE m.name IN ($METRIC_IN)
  AND ts.embargo IS NOT NULL;"

X_DATETIME="$(sqlite3 "$DB_PATH" "$X_TIME_SQL")"

if [[ -z "$X_DATETIME" ]]; then
    print_header "Run List"
    echo "No non-null embargo values were found for Childhood vaccinations metrics."
    echo "Embargo time travel cannot hide rows for this dataset right now."
    echo
    echo "You can still test plumbing:"
    echo "1. Open Childhood vaccinations in CMS."
    echo "2. Set Embargo Time Travel to any datetime and click Preview."
    echo "3. Confirm preview URL contains et=<epoch>."
    echo "4. Confirm page content is unchanged (expected, because no data embargo exists)."
    exit 0
fi

X_COMPARE_SQL="SELECT
    m.name AS metric_name,
    SUM(CASE WHEN ts.embargo > '$X_DATETIME' THEN 1 ELSE 0 END) AS hidden_at_x,
    SUM(CASE WHEN ts.embargo <= '$X_DATETIME' OR ts.embargo IS NULL THEN 1 ELSE 0 END) AS visible_at_x,
    SUM(CASE WHEN ts.embargo > datetime('now') THEN 1 ELSE 0 END) AS hidden_at_now,
    SUM(CASE WHEN ts.embargo <= datetime('now') OR ts.embargo IS NULL THEN 1 ELSE 0 END) AS visible_at_now
FROM data_coretimeseries ts
JOIN data_metric m ON m.id = ts.metric_id
WHERE m.name IN ($METRIC_IN)
GROUP BY m.name
ORDER BY m.name;"

print_header "SQL Evidence For Expectations At X And At Now"
run_sql "$X_TIME_SQL"
run_sql "$X_COMPARE_SQL"

HIDDEN_AT_X_SQL="SELECT m.name
FROM data_coretimeseries ts
JOIN data_metric m ON m.id = ts.metric_id
WHERE m.name IN ($METRIC_IN)
GROUP BY m.name
HAVING SUM(CASE WHEN ts.embargo > '$X_DATETIME' THEN 1 ELSE 0 END) > 0
ORDER BY m.name;"

VISIBLE_AT_X_SQL="SELECT m.name
FROM data_coretimeseries ts
JOIN data_metric m ON m.id = ts.metric_id
WHERE m.name IN ($METRIC_IN)
GROUP BY m.name
HAVING SUM(CASE WHEN ts.embargo <= '$X_DATETIME' OR ts.embargo IS NULL THEN 1 ELSE 0 END) > 0
ORDER BY m.name;"

mapfile -t HIDDEN_AT_X < <(sqlite3 "$DB_PATH" "$HIDDEN_AT_X_SQL")
mapfile -t VISIBLE_AT_X < <(sqlite3 "$DB_PATH" "$VISIBLE_AT_X_SQL")

print_header "Run List (UI Test Steps)"
echo "Scenario 1: Embargoes Re-Applied By Time Travel Backwards"
echo
echo "Use these page ids:"
echo "- Composite page id: $COMPOSITE_PAGE_ID"
echo "- Topic page id: $TOPIC_PAGE_ID"
echo
echo "Set embargo_time to X datetime (UTC): $X_DATETIME"
echo
echo "1) In CMS, open Childhood vaccinations and click Embargo Time Travel."
echo "2) Set the datetime to: $X_DATETIME"
echo "3) Click Preview."
echo "4) Expected in frontend at X:"
if [[ ${#HIDDEN_AT_X[@]} -gt 0 ]]; then
    echo "   - Metrics expected to be missing/reduced (hidden rows exist at X):"
    for metric in "${HIDDEN_AT_X[@]}"; do
        echo "     * $metric"
    done
else
    echo "   - No metrics are expected to be hidden at X (dataset currently fully released at X)."
fi
if [[ ${#VISIBLE_AT_X[@]} -gt 0 ]]; then
    echo "   - Metrics expected to still show (some visible rows at X):"
    for metric in "${VISIBLE_AT_X[@]}"; do
        echo "     * $metric"
    done
fi
echo "5) Set Embargo Time Travel back to now and click Preview again."
echo "6) Expected at now:"
echo "   - Any metric hidden at X due to later embargo should reappear if now is past its embargo."
echo "   - Metrics with null embargo remain visible in both views."
echo

echo "Tip: SQL above is the evidence source for the expected differences."
