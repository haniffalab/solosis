#!/bin/bash

set -e  

if [ -z "$1" ]; then
  echo "No sample ID provided" >&2
  exit 1
fi

if [ -z "$2" ]; then
  echo "No report file path provided" >&2
  exit 1
fi

if ! module load cellgen/irods; then
  echo "Failed to load irods module" >&2
  exit 1
fi

SAMPLE=$1
REPORT_PATH=$2

imeta qu -d -z /seq sample = "$SAMPLE" | grep "^collection: " | sed 's/^collection: //' | awk '{print "CRAM," $0}' > "$REPORT_PATH"
imeta qu -C -z /seq/illumina sample = "$SAMPLE" | grep "^collection: " | sed 's/^collection: //' | awk '{print "CellRanger," $0}' >> "$REPORT_PATH"
echo "Report saved to $REPORT_PATH"

chmod g+w "$REPORT_PATH" 2>/dev/null
exit 0
