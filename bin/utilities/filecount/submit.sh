#!/bin/bash

# Define a function to generate an HTML table
generate_html_table() {
    local data=("$@")

    # Begin HTML table
    echo "<html><body>"
    echo "<table border='1' cellpadding='5' cellspacing='0'>"
    echo "<tr><th>Workspace</th><th>File Count</th><th>File Limit</th></tr>"

    # Add rows
    for row in "${data[@]}"; do
        # Split the row into columns
        echo "<tr><td>${row// /</td><td>}</td></tr>"
    done

    # End HTML table
    echo "</table>"
    echo "</body></html>"
}

# Main script execution
# lustre
#lfs quota -g team298 -h /lustre/scratch126
file_count=$(lfs quota -g team298 -h /lustre/scratch126 | sed -n '4p' | awk '{print $5}')
file_limit=$(lfs quota -g team298 -h /lustre/scratch126 | sed -n '4p' | awk '{print $7}')

# nfs
# df -h /nfs/team298
#nfs_count=$(find /nfs/team298 -type f | wc -l)
nfs_count=345678
nfs_lim=1500000

#warehouse
#df -h /warehouse/team298_wh01
wh_count=$(find /warehouse/team298_wh01 -type f | wc -l)
wh_lim=150000

data=(
    "Lustre $file_count $file_limit"
    "nfs $nfs_count $nfs_lim"
    "warehouse $wh_count $wh_lim"
)

# Generate the HTML table
html_table=$(generate_html_table "${data[@]}")

# Print the table to verify (for debugging)
#echo "$html_table"
email_body=$(cat <<EOF
<html>
<body>
<p>Dear $USER,</p>
<p>The file count for Team298 workspaces:</p>
$html_table
</body>
</html>
EOF
)
recipients=("louiseegrimble@gmail.com" "$USER@sanger.ac.uk")
#recipients=("nlg143@newcastle.ac.uk" "daniela.basurto-lozada@newcastle.ac.uk" "Dave.Horsfall@newcastle.ac.uk" "vm11@sanger.ac>
subject="filecount"
# Message for the email
{
    echo "Subject: $subject"
    echo "To: ${recipients[*]}"
    echo "Content-Type: text/html"
    echo
    echo "$email_body"
} | sendmail "${recipients[@]}"
# Message to confirm email has been sent to email
echo "Script completed. Email sent to nlg143@newcastle.ac.uk"