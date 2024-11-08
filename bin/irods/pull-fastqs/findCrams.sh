#!/bin/bash

# Check if a sample ID file is provided as an argument
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <sample_id_file>"
  exit 1
fi

SAMPLE_FILE="$1"

# Loop through each sample ID in the file
while read -r SAMPLE_ID; do
  echo "Searching for CRAM files for sample ID: $SAMPLE_ID"
  
  # Find CRAM paths using `imeta` command
  CRAM_PATHS=$(imeta qu -z seq -d sample = "$SAMPLE_ID" and target = 1 and type != "fastq" | \
               grep -v "No rows found" | \
               sed 's/collection: //g' | \
               sed 's/dataObj: //g' | \
               grep -v -- '---' | \
               paste -d '/' - - | \
               grep -v "#888.cram" | \
               grep -v "yhuman")

  # Check if any CRAM paths were found
  if [ -z "$CRAM_PATHS" ]; then
    echo "Warning: No CRAM files found for sample $SAMPLE_ID"
  else
    echo "CRAM file paths for $SAMPLE_ID:"
    echo "$CRAM_PATHS"
  fi

done < "$SAMPLE_FILE"

echo "Script completed."
