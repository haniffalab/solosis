#!/bin/bash

# Fixed GitHub repository URL
GITHUB_REPO_URL="https://github.com/haniffalab/solosis"

# Ensure DEPLOY_DIR environment variable is set
if [ -z "$DEPLOY_DIR" ]; then
  echo "Error: Please set the DEPLOY_DIR environment variable."
  exit 1
fi

# Step 1: Fetch the download URL for the release
if [ -z "$RELEASE_TAG" ]; then
  echo "Fetching the latest release..."
  
  # Fetch the latest release info
  RELEASE_INFO=$(curl -s https://api.github.com/repos/haniffalab/solosis/releases/latest)
  
  # Extract the tarball URL and the release tag
  DOWNLOAD_URL=$(echo "$RELEASE_INFO" | grep "tarball_url" | cut -d '"' -f 4)
  RELEASE_TAG=$(echo "$RELEASE_INFO" | grep '"tag_name"' | cut -d '"' -f 4)
  
  echo "Deploying latest release: $RELEASE_TAG"
else
  echo "Fetching release tag: $RELEASE_TAG..."
  DOWNLOAD_URL="https://github.com/haniffalab/solosis/archive/refs/tags/$RELEASE_TAG.tar.gz"
  
  echo "Deploying specific release: $RELEASE_TAG"
fi

TAR_FILE="release.tar.gz"

# Step 2: Remove old contents from the deployment directory, if any
echo "Cleaning up old release files in $DEPLOY_DIR..."
rm -rf $DEPLOY_DIR/*

# Step 3: Download the release package from GitHub
echo "Downloading release from GitHub..."
wget -q -O $TAR_FILE $DOWNLOAD_URL

# Step 4: Extract the tarball directly to the deployment directory, stripping the top-level directory
echo "Extracting the tarball..."
mkdir -p $DEPLOY_DIR
tar --strip-components=1 -xzf $TAR_FILE -C $DEPLOY_DIR

# Step 5: Clean up the downloaded tarball
echo "Cleaning up..."
rm $TAR_FILE

# Step 6: Set permissions
echo "Setting permissions..."
chmod -R -f g+ws $DEPLOY_DIR  # Set group write and setgid permissions

# Step 7: Deployment complete
echo "Deployment of release $RELEASE_TAG complete!"