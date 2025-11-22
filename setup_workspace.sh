#!/bin/bash
# setup_workspace.sh
# Run this from your root workspace folder: ./setup_workspace.sh

echo "🚀 Initializing Unified Scaffolding Workspace..."

# 1. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment exists."
fi

# 2. Activate & Install Dependencies
source venv/bin/activate
echo "⬇️  Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Create Directory Structure
echo "Mw Creating project structure..."
mkdir -p repos
mkdir -p src/analysis
mkdir -p .vscode
mkdir -p docs/adr
mkdir -p observability

# 4. Generate VS Code Workspace File if missing
if [ ! -f "multi-repo-scaffold.code-workspace" ]; then
    echo "📝 Generating VS Code Workspace config..."
    cat <<EOT >> multi-repo-scaffold.code-workspace
{
	"folders": [
		{
			"path": "."
		}
	],
	"settings": {
		"python.defaultInterpreterPath": "\${workspaceFolder}/venv/bin/python",
		"python.terminal.activateEnvironment": true,
		"editor.formatOnSave": true,
        "files.exclude": {
            "**/.git": true,
            "**/__pycache__": true,
            "**/.DS_Store": true
        }
	}
}
EOT
fi

echo "✅ Setup Complete!"
echo "👉 Run 'code multi-repo-scaffold.code-workspace' to open VS Code."
