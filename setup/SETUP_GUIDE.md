# Exam Preparation Agent - Setup Guide

This comprehensive guide will help you set up and verify your development environment for the Exam Preparation Agent Workshop.

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [What the Script Does](#what-the-script-does)
- [Prerequisites](#prerequisites)
- [Installation Instructions](#installation-instructions)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Common Issues](#common-issues)

---

## Quick Start

### Step 1: Run the Setup Verification Script

**Windows:**
```cmd
cd setup
setup_check.bat
```

**macOS / Linux:**
```bash
cd setup
./setup_check.sh
```

**Or directly with Python:**
```bash
cd setup
python3 setup_check.py
```

### Step 2: Fix Any Issues

The script will tell you exactly what needs to be installed or configured. Follow the on-screen instructions or see the detailed [Installation Instructions](#installation-instructions) below.

### Step 3: Follow README

Once all checks pass, return to the main [README.md](../README.md) for instructions on running the application.

---

## What the Script Does

The setup verification script performs comprehensive checks and setup tasks:

### ✅ Automated Checks

1. **Python Version** - Verifies Python 3.11+ is installed
2. **Node.js Version** - Verifies Node.js 22+ is installed
3. **npm** - Checks if npm is available (comes with Node.js)
4. **nvm** - Checks if Node Version Manager is installed
5. **uv** - Checks if uv (Python package manager) is installed
6. **git** - Checks if git version control is installed
7. **Project Structure** - Verifies all required files and directories exist
8. **Environment Configuration** - Checks .env file and required variables
9. **Dependencies** - Tests if backend and frontend dependencies can be installed

### 🔧 Automated Setup

The script can automatically:
- **Create .env file** from template if it doesn't exist
- **Offer to install uv** if it's missing (with your permission)
- **Test dependency installation** to catch issues early

### 📋 Clear Guidance

For anything that can't be automated, the script provides:
- Step-by-step installation instructions for your operating system
- Links to official documentation
- Environment variable setup guidance
- Clear explanations of what each component does

### 🎨 Color-Coded Output

- 🟢 **Green ✓** - Check passed successfully
- 🔴 **Red ✗** - Required component is missing or incorrect
- 🔵 **Blue ℹ** - Information message

---

## Prerequisites

All of the following are **required**:

### 1. Python 3.11+
The backend is written in Python and requires version 3.11 or higher.

**Check your version:**
```bash
python --version
# or
python3 --version
```

### 2. Node.js 22+
The frontend uses React and Vite, which require Node.js 22 or higher.

**Check your version:**
```bash
node --version
```

### 3. nvm (Node Version Manager)
Required for managing Node.js versions. Makes it easy to switch between Node versions.

**Check if installed:**
```bash
nvm --version
```

### 4. npm
Node Package Manager - comes with Node.js installation.

**Check your version:**
```bash
npm --version
```

### 5. uv
Fast Python package manager from Astral.

**Check if installed:**
```bash
uv --version
```

### 6. git
Version control system.

**Check if installed:**
```bash
git --version
```

### 7. Environment Variables

Required in your `.env` file:
- **OPENAI_API_KEY** - For AI features
- **NOTION_TOKEN** - For Notion integration
- **EXAM_PREP_VECTOR_STORE_ID** - For document storage (can be auto-created)
- **LOGFIRE_TOKEN** - For monitoring and logging (optional)

---

## Installation Instructions

### Python 3.11+

#### Windows
**Option 1: Using winget (recommended)**
```cmd
winget install Python.Python.3.11
```

**Option 2: Direct download**
Download from https://www.python.org/downloads/

#### macOS
**Using Homebrew (recommended)**
```bash
brew install python@3.11
```

**Direct download**
Download from https://www.python.org/downloads/

#### Linux
**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11
```

**Fedora:**
```bash
sudo dnf install python3.11
```

**Using pyenv (recommended for multiple versions):**
```bash
curl https://pyenv.run | bash
pyenv install 3.11
pyenv global 3.11
```

---

### nvm (Node Version Manager)

#### Windows
Download and install nvm-windows from:
https://github.com/coreybutler/nvm-windows/releases

After installation:
```cmd
nvm install 22
nvm use 22
```

#### macOS / Linux
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

**After installation, restart your terminal, then:**
```bash
nvm install 22
nvm use 22
```

**To make Node.js 22 the default:**
```bash
nvm alias default 22
```

---

### Node.js 22+

**If you installed nvm (recommended):**
```bash
nvm install 22
nvm use 22
```

**Direct installation (if you didn't use nvm):**
- Windows: Download from https://nodejs.org/
- macOS: `brew install node@22`
- Linux: Use your package manager or https://nodejs.org/

---

### uv (Python Package Manager)

The setup script can install this for you automatically, or:

#### Windows (PowerShell)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

#### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Documentation:** https://docs.astral.sh/uv/getting-started/installation/

---

### git

#### Windows
**Option 1: Using winget**
```cmd
winget install Git.Git
```

**Option 2: Direct download**
Download from https://git-scm.com/download/win

#### macOS
**Install Xcode Command Line Tools (includes git):**
```bash
xcode-select --install
```

**Or using Homebrew:**
```bash
brew install git
```

#### Linux
**Ubuntu/Debian:**
```bash
sudo apt install git
```

**Fedora:**
```bash
sudo dnf install git
```

---

## Environment Configuration

### Setting Up Your .env File

The setup script will create a `.env` file from the template if it doesn't exist. You need to fill in the required values:

### 1. OPENAI_API_KEY (Required)

**Get your API key:**
1. Visit https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)
4. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

### 2. NOTION_TOKEN (Required)

**Create a Notion integration:**
1. Visit https://www.notion.so/my-integrations
2. Click "New integration"
3. Give it a name and select your workspace
4. Copy the "Internal Integration Secret"
5. Add to `.env`:
   ```
   NOTION_TOKEN=secret_your-token-here
   ```

**Important:** Don't forget to share your Notion pages with the integration!

**Detailed guide:** https://github.com/makenotion/notion-mcp-server/blob/main/README.md

### 3. EXAM_PREP_VECTOR_STORE_ID (Required)

**Option A: Let it auto-create (recommended)**
Keep the placeholder value:
```
EXAM_PREP_VECTOR_STORE_ID=vs_your-vector-store-id-here
```
The backend will automatically create a vector store on first run.

**Option B: Create manually**
1. Visit https://platform.openai.com/storage/vector_stores
2. Click "Create vector store"
3. Give it a name
4. Copy the ID (starts with `vs_`)
5. Add to `.env`:
   ```
   EXAM_PREP_VECTOR_STORE_ID=vs_your-id-here
   ```

### 4. LOGFIRE_TOKEN (Optional)

**Set up Logfire monitoring:**
1. Visit https://logfire-us.pydantic.dev/login
2. Sign in with your preferred method
3. Click "Let's go" to use default 'starter-project'
4. Copy the "Write token"
5. Add to `.env`:
   ```
   LOGFIRE_TOKEN=your-token-here
   ```

---

## Running the Application

Once all setup checks pass, you can run the application.

### Option 1: Start Everything Together
```bash
npm start
```
This starts both backend and frontend simultaneously.

### Option 2: Start Separately

**Terminal 1 - Backend:**
```bash
npm run backend
```

**Terminal 2 - Frontend:**
```bash
npm run frontend
```

### Access the Application

- **Frontend:** http://localhost:5173 (or similar port shown in terminal)
- **Backend API:** http://localhost:8002
- **API Documentation:** http://localhost:8002/docs

### Optional: MCP Servers

For advanced features, you can also run:

```bash
# Notion MCP server
npm run notionmcp
```

---

## Troubleshooting

### General Tips

1. **Read error messages carefully** - They often contain the solution
2. **Run the setup script again** after making changes - It's safe to run multiple times
3. **Restart your terminal** after installing new software
4. **Check permissions** - Some installations may require administrator/sudo rights
5. **Verify internet connection** - Required for downloading dependencies
6. **Check firewall/antivirus** - May block installations or downloads

### Script Won't Run

**Issue:** Setup script won't execute

**Windows:**
- Ensure Python is installed: `python --version`
- Run from Command Prompt or PowerShell
- Try: `python setup\setup_check.py`

**macOS/Linux:**
- Ensure script is executable: `chmod +x setup/setup_check.sh`
- Ensure Python 3 is installed: `python3 --version`
- Try: `python3 setup/setup_check.py`

### Command Not Found After Installation

**Issue:** Just installed a tool but terminal says "command not found"

**Solution:**
1. Close and reopen your terminal/command prompt
2. On Windows, you may need to restart your computer
3. Check that the installation directory is in your PATH
4. For nvm on Unix, make sure to restart terminal or run:
   ```bash
   source ~/.bashrc  # or ~/.zshrc for zsh
   ```

### Colors Not Showing

**Issue:** Output has strange characters or no colors

**Solution:**
- Windows: Use Windows Terminal, PowerShell, or Command Prompt (Windows 10+)
- Colors are automatically disabled on older Windows versions
- The script will still work, just without colors

### Permission Errors

**Issue:** "Permission denied" or "Access denied" errors

**Solution:**
- Windows: Run Command Prompt or PowerShell as Administrator
- macOS/Linux: Use `sudo` for system-wide installations
- For Python packages, use `uv` without sudo
- Make sure you have write access to the project directory

---

## Common Issues

### Issue: Python version too old

**Symptoms:** Setup script reports Python 3.10 or older

**Solution:**
Install Python 3.11 or newer using the instructions above. You can have multiple Python versions installed.

---

### Issue: Node.js version too old

**Symptoms:** Setup script reports Node.js version below 22

**Solution:**
1. Install nvm using the instructions above
2. Run: `nvm install 22 && nvm use 22`
3. Run setup script again

---

### Issue: nvm not found

**Symptoms:** Setup script says nvm is not installed

**Windows Solution:**
- Install nvm-windows from https://github.com/coreybutler/nvm-windows/releases
- Restart your terminal
- Run: `nvm install 22 && nvm use 22`

**macOS/Linux Solution:**
- Install using: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash`
- Restart your terminal or run: `source ~/.bashrc`
- Run: `nvm install 22 && nvm use 22`

---

### Issue: uv not found

**Symptoms:** Setup script says uv is not installed

**Solution:**
The script will offer to install it automatically. If that fails:

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your terminal.

---

### Issue: git not found

**Symptoms:** Setup script says git is not installed

**Solution:**
- Windows: `winget install Git.Git` or download from https://git-scm.com/
- macOS: `xcode-select --install` or `brew install git`
- Linux: `sudo apt install git` (Ubuntu/Debian) or `sudo dnf install git` (Fedora)

Then restart your terminal.

---

### Issue: Environment variables not set

**Symptoms:** Setup script reports missing or invalid environment variables

**Solution:**
1. Edit the `.env` file in the project root
2. Add the required API keys (see [Environment Configuration](#environment-configuration))
3. Save the file
4. Run the setup script again to verify

---

### Issue: Backend dependencies fail to install

**Symptoms:** Error when running `uv sync` or setup script fails on backend dependencies

**Solution:**
1. Ensure Python 3.11+ is installed
2. Ensure `uv` is installed and up to date
3. Try manually: `cd backend && uv sync`
4. Check for error messages about missing system libraries
5. On Linux, you may need to install: `sudo apt install python3-dev build-essential`

---

### Issue: Frontend dependencies fail to install

**Symptoms:** Error when running `npm install` or setup script fails on frontend dependencies

**Solution:**
1. Ensure Node.js 22+ is installed
2. Delete `frontend/node_modules` if it exists
3. Delete `frontend/package-lock.json` if it exists
4. Try manually: `cd frontend && npm install`
5. Check for error messages about permissions or disk space

---

### Issue: Port already in use

**Symptoms:** "Port 8002 already in use" or "Port 5173 already in use"

**Solution:**
1. Find and stop the process using the port
2. **Windows:** Use Task Manager or `netstat -ano | findstr :8002`
3. **macOS/Linux:** `lsof -ti:8002 | xargs kill -9`
4. Or change the port in the configuration files

---

## Re-running the Script

It's safe and recommended to run the setup script multiple times:

- ✅ After making any changes to your environment
- ✅ After installing missing prerequisites
- ✅ On a new system or after system updates
- ✅ When troubleshooting issues
- ✅ To verify everything is still configured correctly

The script will never overwrite your `.env` file or delete any data.

---

## Script Features

### Cross-Platform Support
Works seamlessly on:
- ✅ Windows 10/11
- ✅ macOS (Intel and Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Fedora, and others)

### Smart Detection
- Automatically detects your operating system
- Provides OS-specific installation instructions
- Handles different terminal types (CMD, PowerShell, Bash, Zsh)

### Safe and Non-Destructive
- Never overwrites existing `.env` file
- Always asks permission before auto-installing anything
- All checks are read-only unless you explicitly approve changes

### Comprehensive Reporting
- Clear summary of what's working and what needs attention
- Detailed instructions for each missing component
- Links to official documentation
- Actionable next steps

---

## Getting More Help

If you're still stuck after trying the above solutions:

1. **Check error messages** - Read them carefully, they often point to the solution
2. **Review the main README** - See [README.md](../README.md) for additional context
3. **Verify internet connection** - Many steps require downloading from the internet
4. **Try each step manually** - Run individual installation commands to isolate issues
5. **Check system requirements** - Ensure your OS is up to date

---

## What Files Are Created

During setup and running the application, these files/directories are created:

- **`.env`** - Environment configuration file (project root)
- **`backend/.venv/`** - Python virtual environment
- **`frontend/node_modules/`** - Node.js packages
- **`data/`** - Application data and uploaded files

All of these are safe and required for the application to run properly.

---

## Success!

Once all checks pass, you'll see:

```
✓ All checks passed! Your system is ready.
```

At this point, you're ready to run the application! Return to the main [README.md](../README.md) for next steps.

---

**Last Updated:** November 2025
**Maintained by:** Workshop Contributors
