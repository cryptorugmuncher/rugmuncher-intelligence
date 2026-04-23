"""
Opencode Launcher - Self-contained within RMI
No external shell calls needed
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

# Opencode is bundled in rmi/integrations/ai_tools/opencode/
RMI_ROOT = Path(__file__).parent.parent.parent.parent
OPENCODE_DIR = RMI_ROOT / "rmi" / "integrations" / "ai_tools" / "opencode"
OPENCODE_BIN = OPENCODE_DIR / "bin" / "opencode"


class OpencodeLauncher:
    """Launch opencode from within RMI - no external dependencies"""
    
    def __init__(self):
        self.opencode_dir = OPENCODE_DIR
        self.opencode_bin = OPENCODE_BIN
        self._verify_installation()
    
    def _verify_installation(self):
        """Verify opencode is properly bundled"""
        if not self.opencode_bin.exists():
            raise FileNotFoundError(
                f"Opencode not found at {self.opencode_bin}. "
                "Run: npm install @opencode-ai/plugin"
            )
    
    def launch(self, project_path: Optional[str] = None, 
               message: Optional[str] = None,
               web_mode: bool = False) -> subprocess.Popen:
        """
        Launch opencode TUI or web interface
        
        Args:
            project_path: Path to project (default: current dir)
            message: Initial message to send
            web_mode: Launch web interface instead of TUI
        """
        cmd = [str(self.opencode_bin)]
        
        if web_mode:
            cmd.append("web")
        elif message:
            cmd.extend(["run", message])
        
        if project_path:
            cmd.append(project_path)
        
        # Set environment to use bundled node_modules
        env = os.environ.copy()
        env["NODE_PATH"] = str(self.opencode_dir / "node_modules")
        
        return subprocess.Popen(
            cmd,
            env=env,
            cwd=str(self.opencode_dir)
        )
    
    def run_command(self, *args: str) -> Dict[str, Any]:
        """Run an opencode command and return result"""
        cmd = [str(self.opencode_bin)] + list(args)
        
        env = os.environ.copy()
        env["NODE_PATH"] = str(self.opencode_dir / "node_modules")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
                cwd=str(self.opencode_dir)
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
    
    def get_version(self) -> str:
        """Get opencode version"""
        result = self.run_command("--version")
        return result.get("stdout", "unknown").strip()
    
    def get_models(self, provider: Optional[str] = None) -> List[str]:
        """Get available models"""
        args = ["models"]
        if provider:
            args.append(provider)
        
        result = self.run_command(*args)
        
        if result.get("success"):
            # Parse model list from stdout
            lines = result["stdout"].strip().split("\n")
            return [line.strip() for line in lines if line.strip()]
        return []
    
    def launch_web(self, port: Optional[int] = None) -> subprocess.Popen:
        """Launch opencode web interface"""
        cmd = [str(self.opencode_bin), "web"]
        
        if port:
            cmd.extend(["--port", str(port)])
        
        env = os.environ.copy()
        env["NODE_PATH"] = str(self.opencode_dir / "node_modules")
        
        return subprocess.Popen(
            cmd,
            env=env,
            cwd=str(self.opencode_dir)
        )
    
    def serve_headless(self, port: int = 8080) -> subprocess.Popen:
        """Run headless opencode server"""
        cmd = [
            str(self.opencode_bin),
            "serve",
            "--port", str(port),
            "--hostname", "0.0.0.0"
        ]
        
        env = os.environ.copy()
        env["NODE_PATH"] = str(self.opencode_dir / "node_modules")
        
        return subprocess.Popen(
            cmd,
            env=env,
            cwd=str(self.opencode_dir)
        )


# Convenience functions
def launch_opencode(project: Optional[str] = None) -> subprocess.Popen:
    """Quick launch opencode TUI"""
    launcher = OpencodeLauncher()
    return launcher.launch(project_path=project)


def launch_web(port: Optional[int] = None) -> subprocess.Popen:
    """Quick launch opencode web"""
    launcher = OpencodeLauncher()
    return launcher.launch_web(port=port)


def opencode_version() -> str:
    """Get opencode version"""
    launcher = OpencodeLauncher()
    return launcher.get_version()


__all__ = [
    "OpencodeLauncher",
    "launch_opencode",
    "launch_web", 
    "opencode_version"
]
