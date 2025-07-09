#!/bin/bash

CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"

PYTHON_SCRIPT="$CURRENT_DIR/__init__.py"
LOG_PATH="$CURRENT_DIR/backup.log"
CRON_TIME="0 11 * * *"
CRON_JOB="$CRON_TIME cd $CURRENT_DIR && python3 $PYTHON_SCRIPT >> $LOG_PATH 2>&1"


TMP_CRON="$(mktemp)"

crontab -l 2>/dev/null | grep -v "$PYTHON_SCRIPT" > "$TMP_CRON"

echo "$CRON_JOB" >> "$TMP_CRON"

crontab "$TMP_CRON"
rm "$TMP_CRON"

echo "Cron job updated to run at 11:00 AM:"
echo "$CRON_JOB"
