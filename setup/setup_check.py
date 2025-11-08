#!/usr/bin/env python3
"""
Cross-Platform Setup Verification Script for Exam Preparation Agent Workshop
Works on Windows, macOS, and Linux

This script:
1. Checks all prerequisites
2. Auto-sets up what's easy (creates .env file from template)
3. Provides clear instructions for manual setup steps
4. Validates the system is ready to run the application
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def disable():
        """Disable colors for Windows CMD that doesn't support ANSI"""
        Colors.HEADER = ""
        Colors.OKBLUE = ""
        Colors.OKCYAN = ""
        Colors.OKGREEN = ""
        Colors.WARNING = ""
        Colors.FAIL = ""
        Colors.ENDC = ""
        Colors.BOLD = ""
        Colors.UNDERLINE = ""


# Enable colors on Windows 10+ and disable for older Windows
if platform.system() == "Windows":
    try:
        # Enable ANSI colors on Windows 10+
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        Colors.disable()


def print_header(text: str):
    """Print a header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print an info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def run_command(cmd: list[str], capture_output: bool = True) -> tuple[bool, str]:
    """
    Run a command and return success status and output

    Args:
        cmd: Command to run as a list of strings
        capture_output: Whether to capture output

    Returns:
        Tuple of (success, output)
    """
    try:
        if capture_output:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(cmd, check=False, timeout=30)
            return result.returncode == 0, ""
    except FileNotFoundError:
        return False, "Command not found"
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_python_version() -> tuple[bool, str]:
    """Check if Python version is 3.11 or higher"""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 11:
        return True, version_str
    return False, version_str


def check_node_version() -> tuple[bool, str]:
    """Check if Node.js version is 22 or higher"""
    success, output = run_command(["node", "--version"])

    if not success:
        return False, "Not installed"

    # Parse version (format: v22.0.0)
    version_str = output.strip().lstrip("v")
    try:
        major_version = int(version_str.split(".")[0])
        if major_version >= 22:
            return True, version_str
        return False, version_str
    except:
        return False, version_str


def check_npm() -> tuple[bool, str]:
    """Check if npm is installed"""
    success, output = run_command(["npm", "--version"])

    if not success:
        return False, "Not installed"

    return True, output.strip()


def check_uv() -> tuple[bool, str]:
    """Check if uv is installed"""
    success, output = run_command(["uv", "--version"])

    if not success:
        return False, "Not installed"

    return True, output.strip()


def check_nvm() -> tuple[bool, str]:
    """Check if nvm is installed"""
    # nvm is a shell function, so we check differently
    if platform.system() == "Windows":
        success, output = run_command(["nvm", "version"])
    else:
        # On Unix, check if nvm directory exists
        nvm_dir = os.path.expanduser("~/.nvm")
        if os.path.exists(nvm_dir):
            return True, "Installed"
        success, output = run_command(["nvm", "--version"])

    if not success:
        return False, "Not installed"

    return True, output.strip()


def check_git() -> tuple[bool, str]:
    """Check if git is installed"""
    success, output = run_command(["git", "--version"])

    if not success:
        return False, "Not installed"

    return True, output.strip()


def get_project_root() -> Path:
    """Get the project root directory"""
    # Script is in setup/ directory, so parent is project root
    return Path(__file__).parent.parent.absolute()


def check_env_file() -> tuple[bool, dict[str, bool]]:
    """Check if .env file exists and has required variables"""
    project_root = get_project_root()
    env_file = project_root / ".env"

    required_vars = {
        "OPENAI_API_KEY": False,
        "NOTION_TOKEN": False,
        "EXAM_PREP_VECTOR_STORE_ID": False,
        "LOGFIRE_TOKEN": False,  # Optional
    }

    if not env_file.exists():
        return False, required_vars

    # Read .env file and check for variables
    try:
        with open(env_file) as f:
            content = f.read()
            for var in required_vars.keys():
                if f"{var}=" in content:
                    # Check if it has a non-placeholder value
                    for line in content.split("\n"):
                        if line.startswith(f"{var}="):
                            value = line.split("=", 1)[1].strip().strip("\"'")
                            if value and not value.startswith("your-") and value != "vs_your-vector-store-id-here":
                                required_vars[var] = True
                            break

        return True, required_vars
    except Exception as e:
        print_error(f"Error reading .env file: {e}")
        return False, required_vars


def create_env_from_template() -> bool:
    """Create .env file from .env.template if it doesn't exist"""
    project_root = get_project_root()
    env_file = project_root / ".env"
    template_file = project_root / ".env.template"

    if env_file.exists():
        print_info(".env file already exists")
        return True

    if not template_file.exists():
        print_warning(".env.template file not found, creating minimal .env file")
        # Create a minimal .env file
        minimal_content = """# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Vector Store Configuration
EXAM_PREP_VECTOR_STORE_ID=vs_your-vector-store-id-here

# Notion Configuration
NOTION_TOKEN=your-notion-token-here

# Logfire Configuration (Optional)
LOGFIRE_TOKEN=your-logfire-token-here

# Logging
LOG_LEVEL=INFO
"""
        try:
            with open(env_file, "w") as f:
                f.write(minimal_content)
            print_success("Created .env file from minimal template")
            return True
        except Exception as e:
            print_error(f"Failed to create .env file: {e}")
            return False

    # Copy template to .env
    try:
        shutil.copy(template_file, env_file)
        print_success("Created .env file from .env.template")
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False


def auto_install_uv() -> bool:
    """Automatically install uv without user prompts"""
    print_info("Auto-installing uv...")

    system = platform.system()

    if system in ["Linux", "Darwin"]:  # Unix-like systems
        cmd = ["curl", "-LsSf", "https://astral.sh/uv/install.sh"]
        try:
            # Download and pipe to sh
            result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                # Pipe to sh
                install_result = subprocess.run(
                    ["sh"], check=False, input=result.stdout, text=True, timeout=120
                )
                if install_result.returncode == 0:
                    print_success("uv installed successfully!")
                    return True
                else:
                    print_warning("uv installation script failed")
                    return False
        except Exception as e:
            print_warning(f"Auto-installation failed: {e}")
            return False

    elif system == "Windows":
        # Try PowerShell with execution policy bypass
        cmd = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            "irm https://astral.sh/uv/install.ps1 | iex",
        ]
        try:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print_success("uv installed successfully!")
                return True
            else:
                print_warning(f"uv installation failed: {result.stderr}")
                return False
        except Exception as e:
            print_warning(f"Auto-installation failed: {e}")
            return False

    return False


def auto_install_git() -> bool:
    """Automatically install git without user prompts"""
    print_info("Auto-installing git...")

    system = platform.system()

    if system == "Windows":
        # Try winget first
        winget_available, _ = run_command(["winget", "--version"])
        if winget_available:
            cmd = ["winget", "install", "--id", "Git.Git", "--accept-package-agreements", "--accept-source-agreements"]
            try:
                result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print_success("git installed successfully via winget!")
                    return True
                else:
                    print_warning(f"winget installation failed: {result.stderr}")
            except Exception as e:
                print_warning(f"winget installation failed: {e}")

        # Fallback: provide download link
        print_warning("Automatic git installation failed. Please install manually:")
        print_info("  Download from: https://git-scm.com/download/win")
        print_info("  Or run: winget install Git.Git")
        return False

    elif system == "Darwin":  # macOS
        # Try Homebrew
        brew_available, _ = run_command(["brew", "--version"])
        if brew_available:
            cmd = ["brew", "install", "git"]
            try:
                result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print_success("git installed successfully via Homebrew!")
                    return True
            except Exception as e:
                print_warning(f"Homebrew installation failed: {e}")

        # Try Xcode Command Line Tools
        print_info("Attempting to install Xcode Command Line Tools (includes git)...")
        cmd = ["xcode-select", "--install"]
        try:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=30)
            # This command returns non-zero if already installed, so we check git after
            git_ok, _ = check_git()
            if git_ok:
                print_success("git is available (via Xcode Command Line Tools)")
                return True
        except Exception:
            pass

        print_warning("Automatic git installation failed. Please install manually:")
        print_info("  Run: xcode-select --install")
        print_info("  Or: brew install git")
        return False

    else:  # Linux
        # Try apt (Debian/Ubuntu)
        apt_available, _ = run_command(["apt", "--version"])
        if apt_available:
            cmd = ["sudo", "apt", "update"]
            try:
                subprocess.run(cmd, check=False, timeout=60)
                cmd = ["sudo", "apt", "install", "-y", "git"]
                result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print_success("git installed successfully via apt!")
                    return True
            except Exception as e:
                print_warning(f"apt installation failed: {e}")

        # Try dnf (Fedora/RHEL)
        dnf_available, _ = run_command(["dnf", "--version"])
        if dnf_available:
            cmd = ["sudo", "dnf", "install", "-y", "git"]
            try:
                result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print_success("git installed successfully via dnf!")
                    return True
            except Exception as e:
                print_warning(f"dnf installation failed: {e}")

        print_warning("Automatic git installation failed. Please install manually:")
        print_info("  Ubuntu/Debian: sudo apt install git")
        print_info("  Fedora: sudo dnf install git")
        return False


def auto_install_node_npm() -> bool:
    """Automatically install Node.js 22+ and npm without user prompts"""
    print_info("Auto-installing Node.js and npm...")

    system = platform.system()

    if system == "Windows":
        # Try winget first for Node.js LTS
        winget_available, _ = run_command(["winget", "--version"])
        if winget_available:
            # Try to install Node.js 22+ specifically
            cmd = ["winget", "install", "--id", "OpenJS.NodeJS.LTS", "--accept-package-agreements", "--accept-source-agreements"]
            try:
                result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=600)
                if result.returncode == 0:
                    # Wait a moment for PATH to update, then check
                    time.sleep(2)
                    node_ok, node_version = check_node_version()
                    npm_ok, npm_version = check_npm()
                    if node_ok and npm_ok:
                        print_success(f"Node.js v{node_version} and npm {npm_version} installed successfully!")
                        return True
                    else:
                        print_warning("Node.js installed but version check failed. Please restart terminal.")
                        return True  # Assume success, user needs to restart
            except Exception as e:
                print_warning(f"winget installation failed: {e}")

        # Fallback: provide instructions
        print_warning("Automatic Node.js installation failed. Please install manually:")
        print_info("  Download from: https://nodejs.org/")
        print_info("  Or run: winget install OpenJS.NodeJS.LTS")
        return False

    else:  # Unix-like systems (macOS, Linux)
        # Try installing nvm first, then Node.js via nvm
        nvm_ok, _ = check_nvm()
        if not nvm_ok:
            print_info("Installing nvm (Node Version Manager)...")
            nvm_install_cmd = [
                "bash",
                "-c",
                "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
            ]
            try:
                result = subprocess.run(nvm_install_cmd, check=False, capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    print_success("nvm installed successfully!")
                    # Source nvm and install Node.js 22
                    nvm_source_cmd = [
                        "bash",
                        "-c",
                        "export NVM_DIR=\"$HOME/.nvm\" && [ -s \"$NVM_DIR/nvm.sh\" ] && . \"$NVM_DIR/nvm.sh\" && nvm install 22 && nvm use 22",
                    ]
                    install_result = subprocess.run(nvm_source_cmd, check=False, capture_output=True, text=True, timeout=300)
                    if install_result.returncode == 0:
                        print_success("Node.js 22 installed via nvm!")
                        print_warning("Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)")
                        return True
                    else:
                        # nvm installed but Node.js installation failed
                        print_warning("nvm installed but Node.js installation failed. Please restart terminal and run: nvm install 22")
            except Exception as e:
                print_warning(f"nvm installation failed: {e}")
        else:
            # nvm is already installed, try to use it
            print_info("Using existing nvm to install Node.js 22...")
            nvm_cmd = [
                "bash",
                "-c",
                "export NVM_DIR=\"$HOME/.nvm\" && [ -s \"$NVM_DIR/nvm.sh\" ] && . \"$NVM_DIR/nvm.sh\" && nvm install 22 && nvm use 22",
            ]
            try:
                result = subprocess.run(nvm_cmd, check=False, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print_success("Node.js 22 installed via nvm!")
                    return True
            except Exception as e:
                print_warning(f"nvm Node.js installation failed: {e}")

        # macOS: Try Homebrew
        if system == "Darwin":
            brew_available, _ = run_command(["brew", "--version"])
            if brew_available:
                cmd = ["brew", "install", "node@22"]
                try:
                    result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=600)
                    if result.returncode == 0:
                        print_success("Node.js installed via Homebrew!")
                        return True
                except Exception as e:
                    print_warning(f"Homebrew installation failed: {e}")

        print_warning("Automatic Node.js installation failed. Please install manually:")
        print_info("  Install nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash")
        print_info("  Then: nvm install 22 && nvm use 22")
        return False


def check_project_structure() -> tuple[bool, list[str]]:
    """Check if all required project directories and files exist"""
    project_root = get_project_root()

    required_paths = [
        "backend/pyproject.toml",
        "backend/app/main.py",
        "frontend/package.json",
        "package.json",
        "README.md",
    ]

    missing = []
    for path in required_paths:
        full_path = project_root / path
        if not full_path.exists():
            missing.append(path)

    return len(missing) == 0, missing


def test_backend_dependencies() -> bool:
    """Test if backend dependencies can be synced"""
    print_info("Testing backend dependency sync (this may take a moment)...")
    project_root = get_project_root()
    backend_dir = project_root / "backend"

    success, _ = run_command(["uv", "sync", "--directory", str(backend_dir)])
    return success


def test_frontend_dependencies() -> bool:
    """Test if frontend dependencies can be installed"""
    print_info("Testing frontend dependency installation (this may take a moment)...")
    project_root = get_project_root()
    frontend_dir = project_root / "frontend"

    success, _ = run_command(["npm", "install", "--prefix", str(frontend_dir)])
    return success


def print_installation_instructions():
    """Print detailed installation instructions for missing prerequisites"""
    print_header("INSTALLATION INSTRUCTIONS")

    system = platform.system()

    print(f"{Colors.BOLD}Python 3.11+{Colors.ENDC}")
    if system == "Windows":
        print("  Download from: https://www.python.org/downloads/")
        print("  Or use: winget install Python.Python.3.11")
    elif system == "Darwin":  # macOS
        print("  Using Homebrew: brew install python@3.11")
        print("  Or download from: https://www.python.org/downloads/")
    else:  # Linux
        print("  Ubuntu/Debian: sudo apt update && sudo apt install python3.11")
        print("  Fedora: sudo dnf install python3.11")
        print("  Or use pyenv: https://github.com/pyenv/pyenv")

    print(f"\n{Colors.BOLD}nvm (Node Version Manager) - Required{Colors.ENDC}")
    if system == "Windows":
        print("  nvm for Windows: https://github.com/coreybutler/nvm-windows/releases")
        print("  After installing, restart terminal and run: nvm install 22 && nvm use 22")
    else:
        print("  Install nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash")
        print("  After installing, restart terminal and run: nvm install 22 && nvm use 22")

    print(f"\n{Colors.BOLD}Node.js 22+ (via nvm){Colors.ENDC}")
    print("  Once nvm is installed:")
    print("  nvm install 22")
    print("  nvm use 22")
    print("  nvm alias default 22")

    print(f"\n{Colors.BOLD}uv (Python Package Manager){Colors.ENDC}")
    if system == "Windows":
        print("  Run in PowerShell: irm https://astral.sh/uv/install.ps1 | iex")
    else:
        print("  Run in terminal: curl -LsSf https://astral.sh/uv/install.sh | sh")
    print("  Documentation: https://docs.astral.sh/uv/getting-started/installation/")

    print(f"\n{Colors.BOLD}git (Version Control) - Required{Colors.ENDC}")
    if system == "Windows":
        print("  Download from: https://git-scm.com/download/win")
        print("  Or use: winget install Git.Git")
    elif system == "Darwin":
        print("  Install Xcode Command Line Tools: xcode-select --install")
        print("  Or using Homebrew: brew install git")
    else:
        print("  Ubuntu/Debian: sudo apt install git")
        print("  Fedora: sudo dnf install git")


def print_env_setup_instructions(env_vars: dict[str, bool]):
    """Print instructions for setting up environment variables"""
    print_header("ENVIRONMENT VARIABLE SETUP")

    project_root = get_project_root()
    env_file = project_root / ".env"

    print(f"Edit the file: {Colors.BOLD}{env_file}{Colors.ENDC}\n")

    if not env_vars["OPENAI_API_KEY"]:
        print(f"{Colors.BOLD}1. OPENAI_API_KEY (Required){Colors.ENDC}")
        print("   - Visit: https://platform.openai.com/api-keys")
        print("   - Create a new API key")
        print("   - Add to .env: OPENAI_API_KEY=sk-...")
        print()

    if not env_vars["NOTION_TOKEN"]:
        print(f"{Colors.BOLD}2. NOTION_TOKEN (Required){Colors.ENDC}")
        print("   - Visit: https://www.notion.so/my-integrations")
        print("   - Click 'New integration'")
        print("   - Give it a name and select workspace")
        print("   - Copy the 'Internal Integration Secret'")
        print("   - Add to .env: NOTION_TOKEN=secret_...")
        print("   - Don't forget to share your Notion pages with the integration!")
        print("   - Guide: https://github.com/makenotion/notion-mcp-server/blob/main/README.md")
        print()

    if not env_vars["EXAM_PREP_VECTOR_STORE_ID"]:
        print(f"{Colors.BOLD}3. EXAM_PREP_VECTOR_STORE_ID (Required){Colors.ENDC}")
        print("   - Option A: Keep placeholder 'vs_your-vector-store-id-here'")
        print("              (Will auto-create on first run)")
        print("   - Option B: Create manually:")
        print("     * Visit: https://platform.openai.com/storage/vector_stores")
        print("     * Click 'Create vector store'")
        print("     * Copy the ID (starts with 'vs_')")
        print("     * Add to .env: EXAM_PREP_VECTOR_STORE_ID=vs_...")
        print()

    if not env_vars["LOGFIRE_TOKEN"]:
        print(f"{Colors.BOLD}4. LOGFIRE_TOKEN (Optional but recommended){Colors.ENDC}")
        print("   - Visit: https://logfire-us.pydantic.dev/login")
        print("   - Sign in with your preferred method")
        print("   - Click 'Lets go' to use default 'starter-project'")
        print("   - Copy the 'Write token'")
        print("   - Add to .env: LOGFIRE_TOKEN=...")
        print()


def print_final_steps():
    """Print final steps to run the application"""
    print_header("FINAL STEPS TO RUN THE APPLICATION")

    print(f"{Colors.BOLD}Once all prerequisites are met:{Colors.ENDC}\n")

    print("1. Start both backend and frontend together:")
    print(f"   {Colors.OKCYAN}npm start{Colors.ENDC}")
    print()

    print("2. Or start them separately:")
    print(f"   Terminal 1 (Backend):  {Colors.OKCYAN}npm run backend{Colors.ENDC}")
    print(f"   Terminal 2 (Frontend): {Colors.OKCYAN}npm run frontend{Colors.ENDC}")
    print()

    print("3. Access the application:")
    print(f"   Frontend: {Colors.OKCYAN}http://localhost:5173{Colors.ENDC} (or similar)")
    print(f"   Backend:  {Colors.OKCYAN}http://localhost:8002{Colors.ENDC}")
    print()

    print(f"{Colors.BOLD}Optional MCP Servers (for advanced features):{Colors.ENDC}")
    print(f"   Notion MCP: {Colors.OKCYAN}npm run notionmcp{Colors.ENDC}")
    print()


def main():
    """Main function to run all checks"""
    print_header("EXAM PREPARATION AGENT - SETUP VERIFICATION")

    system_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
    print(f"{Colors.BOLD}System:{Colors.ENDC} {system_info}\n")

    # Track overall status
    all_checks_passed = True
    warnings = []

    # Check Python version
    print(f"{Colors.BOLD}Checking Python...{Colors.ENDC}")
    python_ok, python_version = check_python_version()
    if python_ok:
        print_success(f"Python {python_version} (requires 3.11+)")
    else:
        print_error(f"Python {python_version} found, but 3.11+ is required")
        all_checks_passed = False

    # Check Node.js
    print(f"\n{Colors.BOLD}Checking Node.js...{Colors.ENDC}")
    node_ok, node_version = check_node_version()
    if node_ok:
        print_success(f"Node.js v{node_version} (requires 22+)")
    else:
        print_warning(f"Node.js {node_version} - Version 22+ is required, attempting auto-installation...")
        if auto_install_node_npm():
            # Re-check
            node_ok, node_version = check_node_version()
            if node_ok:
                print_success(f"Node.js v{node_version} installed!")
            else:
                print_warning("Node.js installation completed but version check failed. Please restart terminal.")
                all_checks_passed = False
        else:
            print_error("Node.js auto-installation failed")
            all_checks_passed = False

    # Check npm
    print(f"\n{Colors.BOLD}Checking npm...{Colors.ENDC}")
    npm_ok, npm_version = check_npm()
    if npm_ok:
        print_success(f"npm {npm_version}")
    else:
        # npm should come with Node.js, but if Node.js was just installed, it might not be in PATH yet
        if not node_ok:
            print_warning("npm not found (should come with Node.js). Please restart terminal after Node.js installation.")
        else:
            print_error("npm not found (should come with Node.js)")
            all_checks_passed = False

    # Check nvm (informational only, not required if Node.js is installed)
    print(f"\n{Colors.BOLD}Checking nvm (optional)...{Colors.ENDC}")
    nvm_ok, nvm_version = check_nvm()
    if nvm_ok:
        print_success(f"nvm {nvm_version}")
    else:
        print_info("nvm not found (optional - Node.js can be installed without it)")

    # Check uv
    print(f"\n{Colors.BOLD}Checking uv...{Colors.ENDC}")
    uv_ok, uv_version = check_uv()
    if uv_ok:
        print_success(f"uv {uv_version}")
    else:
        print_warning("uv not found - attempting auto-installation...")
        if auto_install_uv():
            # Re-check
            uv_ok, uv_version = check_uv()
            if uv_ok:
                print_success(f"uv {uv_version} installed!")
            else:
                print_warning("uv installation completed but not found in PATH. Please restart terminal.")
                all_checks_passed = False
        else:
            print_error("uv auto-installation failed")
            all_checks_passed = False

    # Check git (required)
    print(f"\n{Colors.BOLD}Checking git (required)...{Colors.ENDC}")
    git_ok, git_version = check_git()
    if git_ok:
        print_success(f"{git_version}")
    else:
        print_warning("git not found - attempting auto-installation...")
        if auto_install_git():
            # Re-check
            git_ok, git_version = check_git()
            if git_ok:
                print_success(f"{git_version} installed!")
            else:
                print_warning("git installation completed but not found in PATH. Please restart terminal.")
                all_checks_passed = False
        else:
            print_error("git auto-installation failed")
            all_checks_passed = False

    # Check project structure
    print(f"\n{Colors.BOLD}Checking project structure...{Colors.ENDC}")
    structure_ok, missing_paths = check_project_structure()
    if structure_ok:
        print_success("All required files and directories present")
    else:
        print_error("Missing required files/directories:")
        for path in missing_paths:
            print(f"  - {path}")
        all_checks_passed = False

    # Check/create .env file
    print(f"\n{Colors.BOLD}Checking environment configuration...{Colors.ENDC}")
    env_exists, env_vars = check_env_file()

    if not env_exists:
        print_warning(".env file not found")
        create_env_from_template()
        # Re-check
        env_exists, env_vars = check_env_file()
    else:
        print_success(".env file exists")

    # Check environment variables (non-blocking - warnings only)
    required_vars_set = all(
        [env_vars["OPENAI_API_KEY"], env_vars["NOTION_TOKEN"], env_vars["EXAM_PREP_VECTOR_STORE_ID"]]
    )

    print(f"\n{Colors.BOLD}Environment Variables (informational):{Colors.ENDC}")
    env_warnings = []
    for var, is_set in env_vars.items():
        if var == "LOGFIRE_TOKEN":  # Optional
            if is_set:
                print_success(f"{var} (optional)")
            else:
                print_warning(f"{var} (optional - not set)")
        elif is_set:
            print_success(var)
        else:
            print_warning(f"{var} - NOT SET (required for application)")
            env_warnings.append(var)
    
    # Add env warnings to warnings list but don't fail the check
    if env_warnings:
        warnings.append(f"Environment variables not set: {', '.join(env_warnings)}")

    # Test dependency installation if prerequisites are met
    if all_checks_passed and uv_ok and npm_ok:
        print(f"\n{Colors.BOLD}Testing dependency installation...{Colors.ENDC}")

        # Test backend
        backend_ok = test_backend_dependencies()
        if backend_ok:
            print_success("Backend dependencies can be installed")
        else:
            print_error("Backend dependency installation failed")
            warnings.append("Backend dependencies may have issues")

        # Test frontend
        frontend_ok = test_frontend_dependencies()
        if frontend_ok:
            print_success("Frontend dependencies can be installed")
        else:
            print_error("Frontend dependency installation failed")
            warnings.append("Frontend dependencies may have issues")

    # Print summary
    print_header("SUMMARY")

    if all_checks_passed:
        print_success(f"{Colors.BOLD}All dependency checks passed! Your system is ready.{Colors.ENDC}")

        if warnings:
            print(f"\n{Colors.BOLD}Warnings:{Colors.ENDC}")
            for warning in warnings:
                print_warning(warning)

        if not required_vars_set:
            print(f"\n{Colors.BOLD}Note:{Colors.ENDC} Environment variables are not fully configured.")
            print_info("The application may not work until you set up the required API keys.")
            print_env_setup_instructions(env_vars)

        print_final_steps()
        return 0
    else:
        print_error(f"{Colors.BOLD}Some dependency checks failed. Please address the issues below.{Colors.ENDC}")

        if warnings:
            print(f"\n{Colors.BOLD}Warnings:{Colors.ENDC}")
            for warning in warnings:
                print_warning(warning)

        print_installation_instructions()

        if not required_vars_set:
            print_env_setup_instructions(env_vars)

        print(f"\n{Colors.BOLD}After fixing the issues, run this script again:{Colors.ENDC}")
        print(f"  {Colors.OKCYAN}python setup_check.py{Colors.ENDC}")
        print()

        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup check cancelled by user.{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
