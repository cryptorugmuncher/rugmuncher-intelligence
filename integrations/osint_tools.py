"""
RMI OSINT Tools Integration
Bundles maigret, deepface, social-analyzer for local use
No external shell calls needed - everything self-contained
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

# Base paths - everything self-contained in RMI
RMI_ROOT = Path(__file__).parent.parent.parent
TOOLS_DIR = RMI_ROOT / "rmi" / "tools"
MAIGRET_DATA = TOOLS_DIR / "maigret" / "data.json"
DEEPCHECK_WEIGHTS = TOOLS_DIR / "deepface" / "weights"
SOCIAL_ANALYZER_DIR = TOOLS_DIR / "social_analyzer"
MUNCHSCAN_DIR = TOOLS_DIR / "munchscan"


class MaigretTool:
    """Local maigret integration - no shell install needed"""
    
    def __init__(self):
        self.data_file = MAIGRET_DATA
        self.sites_data = None
        self._load_data()
    
    def _load_data(self):
        """Load maigret site data locally"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.sites_data = json.load(f)
    
    def search_username(self, username: str, sites: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search username across platforms
        Uses local maigret if available, falls back to data.json
        """
        results = {
            "username": username,
            "found": [],
            "not_found": [],
            "errors": []
        }
        
        # Try local maigret binary first
        maigret_bin = Path.home() / ".local" / "bin" / "maigret"
        if maigret_bin.exists():
            try:
                cmd = [str(maigret_bin), username, "--json", "--timeout", "10"]
                if sites:
                    cmd.extend(["--site", ",".join(sites)])
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    return json.loads(result.stdout)
            except Exception as e:
                results["errors"].append(str(e))
        
        # Fallback: use local data.json
        if self.sites_data and "sites" in self.sites_data:
            for site_name, site_info in self.sites_data["sites"].items():
                if sites and site_name not in sites:
                    continue
                    
                check_url = site_info.get("urlProbe", site_info.get("urlMain", ""))
                if check_url and username:
                    profile_url = check_url.replace("{username}", username)
                    results["found"].append({
                        "site": site_name,
                        "url": profile_url,
                        "status": "check_required"
                    })
        
        return results
    
    def get_supported_sites(self) -> List[str]:
        """Get list of supported sites from local data"""
        if self.sites_data and "sites" in self.sites_data:
            return list(self.sites_data["sites"].keys())
        return []


class DeepfaceTool:
    """Local deepface integration - uses local weights"""
    
    def __init__(self):
        self.weights_dir = DEEPCHECK_WEIGHTS
        self._setup_local_weights()
    
    def _setup_local_weights(self):
        """Configure deepface to use local weights"""
        os.environ["DEEPFACE_HOME"] = str(TOOLS_DIR / "deepface")
    
    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """Verify if two faces match"""
        try:
            from deepface import DeepFace
            
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                enforce_detection=False
            )
            
            return {
                "verified": result.get("verified", False),
                "distance": result.get("distance", 1.0),
                "threshold": result.get("threshold", 0.6),
                "model": result.get("model", "unknown"),
                "error": None
            }
        except Exception as e:
            return {
                "verified": False,
                "error": str(e)
            }
    
    def analyze_face(self, img_path: str) -> Dict[str, Any]:
        """Analyze face attributes"""
        try:
            from deepface import DeepFace
            
            result = DeepFace.analyze(
                img_path=img_path,
                actions=['age', 'gender', 'emotion', 'race'],
                enforce_detection=False
            )
            
            return {
                "analysis": result,
                "error": None
            }
        except Exception as e:
            return {
                "analysis": None,
                "error": str(e)
            }


class SocialAnalyzerTool:
    """Social analyzer integration"""
    
    def __init__(self):
        self.app_dir = SOCIAL_ANALYZER_DIR
        self.app_js = self.app_dir / "app.js"
        self.app_py = self.app_dir / "app.py"
    
    def analyze(self, username: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Run social analyzer on username"""
        results = {"username": username, "findings": []}
        
        # Try Python version first
        if self.app_py.exists():
            try:
                cmd = ["python3", str(self.app_py), "--username", username, "--json"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(self.app_dir)
                )
                
                if result.returncode == 0:
                    return json.loads(result.stdout)
            except Exception as e:
                results["error"] = str(e)
        
        # Try Node version
        if self.app_js.exists():
            try:
                cmd = ["node", str(self.app_js), "--username", username]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(self.app_dir)
                )
                
                if result.returncode == 0:
                    return {"output": result.stdout}
            except Exception as e:
                results["error"] = str(e)
        
        return results


class MunchscanTool:
    """Munchscan integration"""
    
    def __init__(self):
        self.src_dir = MUNCHSCAN_DIR / "src"
    
    def scan(self, target: str, scan_type: str = "basic") -> Dict[str, Any]:
        """Run munchscan on target"""
        results = {"target": target, "scan_type": scan_type, "results": []}
        
        # Look for main entry point
        main_files = list(self.src_dir.glob("*.js")) if self.src_dir.exists() else []
        
        if main_files:
            try:
                cmd = ["node", str(main_files[0]), target, scan_type]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                results["output"] = result.stdout
                results["errors"] = result.stderr if result.stderr else None
                results["returncode"] = result.returncode
            except Exception as e:
                results["error"] = str(e)
        else:
            results["error"] = "No munchscan entry point found"
        
        return results


# Convenience functions for quick access
def search_username(username: str) -> Dict[str, Any]:
    """Quick username search across platforms"""
    tool = MaigretTool()
    return tool.search_username(username)


def verify_faces(img1: str, img2: str) -> Dict[str, Any]:
    """Quick face verification"""
    tool = DeepfaceTool()
    return tool.verify_face(img1, img2)


def analyze_social(username: str) -> Dict[str, Any]:
    """Quick social media analysis"""
    tool = SocialAnalyzerTool()
    return tool.analyze(username)


# Export main classes
__all__ = [
    "MaigretTool",
    "DeepfaceTool", 
    "SocialAnalyzerTool",
    "MunchscanTool",
    "search_username",
    "verify_faces",
    "analyze_social"
]
