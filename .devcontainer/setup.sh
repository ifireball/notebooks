#!/bin/bash

# =============================================================================
# Development Environment Setup Script
# =============================================================================
# This script runs after the dev container is created and the workspace is mounted.
# It handles project-specific setup that requires access to pyproject.toml and
# cannot be done in the Containerfile (since the workspace isn't available there).
#
# DESIGN DECISIONS:
# 1. Run after container creation (not during build) to access workspace files
# 2. Use uv for all Python operations (consistent with our package management choice)
# 3. Set up Jupyter kernel for seamless notebook development
# 4. Configure optional development tools (pre-commit) if available
# 5. Provide helpful usage information for common development tasks

set -e  # Exit on any error

echo "Setting up Python development environment with uv..."
echo "Using Fedora 42 with Python 3.12 (will switch to quay.io/fedora when images available)"

# =============================================================================
# Project Setup
# =============================================================================
# Ensure we're working in the correct directory (workspace root)
cd /workspace

# Install all project dependencies including development tools
# DECISION: Use --dev to install both main and development dependencies
# This includes pytest, black, mypy, ruff, etc. defined in pyproject.toml
echo "Installing Python dependencies..."
uv sync --dev

# =============================================================================
# Jupyter Configuration (Optional)
# =============================================================================
# NOTE: VS Code typically auto-detects and creates Jupyter kernels when opening notebooks
# This manual setup is only needed for:
# - Direct Jupyter Lab usage (outside VS Code)
# - Custom kernel naming/configuration
# - Ensuring kernel availability before first notebook use

# Check if user wants manual Jupyter kernel setup
if [ "${SETUP_JUPYTER_KERNEL:-false}" = "true" ]; then
    echo "Setting up Jupyter kernel (set SETUP_JUPYTER_KERNEL=false to skip)..."
    uv run python -m ipykernel install --user --name=notebooks --display-name="Notebooks (uv)" || {
        echo "Jupyter kernel setup failed (not critical - VS Code will auto-create kernels)"
    }
else
    echo "Skipping manual Jupyter kernel setup (VS Code will auto-detect)"
fi

# =============================================================================
# Development Tools Setup
# =============================================================================
# Set up pre-commit hooks if the package is available
# DECISION: Make this optional since not all projects use pre-commit
# DECISION: Use conditional check to avoid errors if pre-commit isn't installed
if uv run python -c "import pre_commit" 2>/dev/null; then
    echo "Setting up pre-commit hooks..."
    uv run pre-commit install || echo "Pre-commit setup skipped (not critical)"
fi

# =============================================================================
# Completion Message
# =============================================================================
echo "Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  uv run jupyter lab              # Start Jupyter Lab (manual kernel useful here)"
echo "  uv run uvicorn counter:app      # Start FastAPI app (from your notebook example)"
echo "  uv run python -m pytest        # Run tests"
echo "  uv sync                         # Sync dependencies"
echo "  uv add <package>                # Add new package"
echo "  uv remove <package>             # Remove package"
echo ""
echo "Notes:"
echo "  - VS Code auto-detects Python kernels when opening .ipynb files"
echo "  - Manual Jupyter kernel is mainly for direct Jupyter Lab usage"
echo "  - Set SETUP_JUPYTER_KERNEL=false to skip kernel setup in future runs" 