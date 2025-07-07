#!/bin/bash

# =============================================================================
# Git Configuration Initialization Script
# =============================================================================
# This script runs before the container starts to ensure git user configuration
# is available in the workspace. It will NOT overwrite existing local config.
#
# Priority order:
# 1. Existing local config (never overwrite)
# 2. Host global config
# 3. Environment variables (GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL, etc.)

echo "Checking git configuration..."

# Check if local config already exists
LOCAL_NAME=$(git config --local --get user.name 2>/dev/null || echo '')
LOCAL_EMAIL=$(git config --local --get user.email 2>/dev/null || echo '')

if [ -n "$LOCAL_NAME" ] && [ -n "$LOCAL_EMAIL" ]; then
    echo "✓ Local git configuration already exists: $LOCAL_NAME <$LOCAL_EMAIL>"
    echo "  Not modifying existing configuration"
    exit 0
fi

# Try to get configuration from host global config
HOST_GLOBAL_NAME=$(git config --global --get user.name 2>/dev/null || echo '')
HOST_GLOBAL_EMAIL=$(git config --global --get user.email 2>/dev/null || echo '')

# Try to get configuration from environment variables
ENV_NAME="${GIT_AUTHOR_NAME:-${GIT_COMMITTER_NAME:-}}"
ENV_EMAIL="${GIT_AUTHOR_EMAIL:-${GIT_COMMITTER_EMAIL:-}}"

# Determine which source to use
SOURCE_NAME=""
SOURCE_EMAIL=""
CONFIG_SOURCE=""

if [ -n "$HOST_GLOBAL_NAME" ] && [ -n "$HOST_GLOBAL_EMAIL" ]; then
    SOURCE_NAME="$HOST_GLOBAL_NAME"
    SOURCE_EMAIL="$HOST_GLOBAL_EMAIL"
    CONFIG_SOURCE="host global config"
elif [ -n "$ENV_NAME" ] && [ -n "$ENV_EMAIL" ]; then
    SOURCE_NAME="$ENV_NAME"
    SOURCE_EMAIL="$ENV_EMAIL"
    CONFIG_SOURCE="environment variables"
fi

# Set local configuration if we found valid source
if [ -n "$SOURCE_NAME" ] && [ -n "$SOURCE_EMAIL" ]; then
    echo "Found git configuration from $CONFIG_SOURCE: $SOURCE_NAME <$SOURCE_EMAIL>"
    
    # Set local git config in the workspace
    git config user.name "$SOURCE_NAME"
    git config user.email "$SOURCE_EMAIL"
    
    echo "✓ Git configuration copied to workspace from $CONFIG_SOURCE"
else
    echo "⚠ Warning: No git user configuration found"
    echo "  Checked:"
    echo "    - Local workspace config"
    echo "    - Host global config (git config --global)"
    echo "    - Environment variables (GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL)"
    echo ""
    echo "  To fix, run one of:"
    echo "    git config --global user.name \"Your Name\""
    echo "    git config --global user.email \"your.email@example.com\""
    echo "  Or set environment variables:"
    echo "    export GIT_AUTHOR_NAME=\"Your Name\""
    echo "    export GIT_AUTHOR_EMAIL=\"your.email@example.com\""
fi 