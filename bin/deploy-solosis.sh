#!/bin/bash

# export DEPLOY_DIR="/software/cellgen/team298/shared/solosis"
# export MODULEFILES_DIR="/software/cellgen/team298/shared/modulefiles"

# GitHub repository URL
GITHUB_REPO_URL="https://github.com/haniffalab/solosis"

# Ensure DEPLOY_DIR environment variable is set
if [ -z "$DEPLOY_DIR" ]; then
  echo "Error: Please set the DEPLOY_DIR environment variable"
  exit 1
fi

# Ensure MODULEFILES_DIR environment variable is set
if [ -z "$MODULEFILES_DIR" ]; then
  echo "Error: Please set the MODULEFILES_DIR environment variable for symlinking"
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
  
  # Strip the 'v' from the release tag if present
  RELEASE_TAG=${RELEASE_TAG#v}
  
  echo "Deploying latest release: $RELEASE_TAG"
else
  echo "Fetching release tag: $RELEASE_TAG..."
  RELEASE_TAG=${RELEASE_TAG#v}
  DOWNLOAD_URL="https://github.com/haniffalab/solosis/archive/refs/tags/v$RELEASE_TAG.tar.gz"
  
  echo "Deploying specific release: $RELEASE_TAG"
fi

# Step 2: Download the release package from GitHub
TAR_FILE="release.tar.gz"
echo "Downloading release from GitHub..."
wget -q -O $TAR_FILE $DOWNLOAD_URL

# Step 3: Remove old contents from the deployment directory
echo "Cleaning up old release files in $DEPLOY_DIR/$RELEASE_TAG..."
rm -rf $DEPLOY_DIR/$RELEASE_TAG/*

# Step 4: Extract the tarball to the deployment directory
echo "Extracting the tarball..."
mkdir -p $DEPLOY_DIR/$RELEASE_TAG
tar --strip-components=1 -xzf $TAR_FILE -C $DEPLOY_DIR/$RELEASE_TAG

# Step 5: Symlink the Modulefile
MODULE_FILE="$DEPLOY_DIR/$RELEASE_TAG/modulefiles/solosis/$RELEASE_TAG"
if [ -f "$MODULE_FILE" ]; then
  echo "Creating symlink for Modulefile..."
  mkdir -p $MODULEFILES_DIR/solosis
  ln -sf "$MODULE_FILE" "$MODULEFILES_DIR/solosis/$RELEASE_TAG"
else
  echo "Warning: Modulefile not found in $DEPLOY_DIR/$RELEASE_TAG/modulefiles/solosis/$RELEASE_TAG"
fi

# Step 6: Clean up the downloaded tarball
echo "Cleaning up..."
rm $TAR_FILE

# Step 7: Set permissions
echo "Setting permissions..."
chmod -R -f g+ws $DEPLOY_DIR  # Set group write and setgid permissions

# Step 8: Deployment complete
echo "Deployment of release $RELEASE_TAG complete!"
