"""
Kimi Code CLI Launcher - Self-contained within RMI
References existing UV installation - no duplication of 226MB
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

# Kimi is installed via UV - we reference it, don't duplicate
RMI_ROOT = Path(__file__).parent.parent.parent.parent
KIMI_SYSTEM_BIN = Path.home() / ".local" / "bin" / "kimi"
KIMI_UV_BIN = Path.home() / ".local" / "share" / "uv" / "tools" / "kimi-cli" / "bin" / "kimi"
KIMI_CONFIG_DIR = RMI_ROOT / "rmi" / "integrations" / "ai_tools" / "kimi_cli"
KIMI_CONFIG_FILE = KIMI_CONFIG_DIR / "config.toml"


class KimiLauncher:
    """Launch Kimi Code CLI from within RMI"""
    
    def __init__(self):
        self.kimi_bin = self._find_kimi_binary()
        self.config_dir = KIMI_CONFIG_DIR
        self._verify_installation()
    
    def _find_kimi_binary(self) -> Path:
        """Find kimi binary (system or UV installed)"""
        # Priority: UV install, then system install
        if KIMI_UV_BIN.exists():
            return KIMI_UV_BIN
        if KIMI_SYSTEM_BIN.exists():
            return KIMI_SYSTEM_BIN
        
        # Try to find in PATH
        for path_dir in os.environ.get("PATH", "").split(":"):
            candidate = Path(path_dir) / "kimi"
            if candidate.exists():
                return candidate
        
        raise FileNotFoundError(
            "Kimi CLI not found. Install with: uv tool install kimi-cli"
        )
    
    def _verify_installation(self):
        """Verify kimi is accessible"""
        if not self.kimi_bin.exists():
            raise FileNotFoundError(f"Kimi not found at {self.kimi_bin}")
    
    def run(self, *args: str, cwd: Optional[str] = None, 
            capture_output: bool = True, timeout: int = 300) -> Dict[str, Any]:
        """
        Run kimi command
        
        Args:
            *args: Command arguments
            cwd: Working directory
            capture_output: Capture stdout/stderr
            timeout: Max execution time
        """
        cmd = [str(self.kimi_bin)] + list(args)
        
        env = os.environ.copy()
        # Use RMI bundled config
        env["KIMI_CONFIG_DIR"] = str(self.config_dir)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                env=env,
                cwd=cwd or str(RMI_ROOT)
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def launch_interactive(self, path: Optional[str] = None) -> subprocess.Popen:
        """Launch interactive kimi session"""
        cmd = [str(self.kimi_bin)]
        if path:
            cmd.append(path)
        
        env = os.environ.copy()
        env["KIMI_CONFIG_DIR"] = str(self.config_dir)
        
        return subprocess.Popen(
            cmd,
            env=env,
            cwd=path or str(RMI_ROOT)
        )
    
    def get_version(self) -> str:
        """Get kimi version"""
        result = self.run("--version")
        return result.get("stdout", "unknown").strip()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current kimi config"""
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib
        
        if self.config_dir.exists():
            config_file = self.config_dir / "config.toml"
            if config_file.exists():
                with open(config_file, "rb") as f:
                    return tomllib.load(f)
        return {}
    
    def update_config(self, updates: Dict[str, Any]):
        """Update kimi config"""
        import toml
        
        config = self.get_config()
        config.update(updates)
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_dir / "config.toml", "w") as f:
            toml.dump(config, f)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List available sessions"""
        sessions_dir = self.config_dir / "sessions"
        sessions = []
        
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*.json"):
                try:
                    with open(session_file) as f:
                        data = json.load(f)
                        sessions.append({
                            "id": session_file.stem,
                            "name": data.get("name", "Unnamed"),
                            "created": data.get("created_at"),
                            "file": str(session_file)
                        })
                except:
                    pass
        
        return sessions
    
    def resume_session(self, session_id: str) -> subprocess.Popen:
        """Resume a specific session"""
        return self.launch_interactive()
    
    def run_yolo(self, prompt: str, path: Optional[str] = None) -> Dict[str, Any]:
        """Run kimi in yolo mode (auto-approve)"""
        return self.run("--yolo", "--", prompt, cwd=path)
    
    def run_with_context(self, prompt: str, files: List[str],
                        path: Optional[str] = None) -> Dict[str, Any]:
        """Run kimi with specific file context"""
        args = []
        for f in files:
            args.extend(["-f", f])
        args.extend(["--", prompt])
        
        return self.run(*args, cwd=path)


# Convenience functions
def kimi(prompt: str, path: Optional[str] = None, yolo: bool = False) -> Dict[str, Any]:
    """Quick kimi execution"""
    launcher = KimiLauncher()
    args = ["--", prompt]
    if yolo:
        args = ["--yolo"] + args
    return launcher.run(*args, cwd=path)


def kimi_interactive(path: Optional[str] = None) -> subprocess.Popen:
    """Launch interactive kimi"""
    launcher = KimiLauncher()
    return launcher.launch_interactive(path)


def kimi_version() -> str:
    """Get kimi version"""
    launcher = KimiLauncher()
    return launcher.get_version()


def kimi_config() -> Dict[str, Any]:
    """Get kimi config"""
    launcher = KimiLauncher()
    return launcher.get_config()


__all__ = [
    "KimiLauncher",
    "kimi",
    "kimi_interactive",
    "kimi_version",
    "kimi_config"
]
