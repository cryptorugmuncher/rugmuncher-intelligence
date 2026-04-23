"""
CPU-Friendly Local LLM Configuration
====================================
Recommendations for 2 small, fast models to run on Contabo VPS.
Optimized for crypto investigation tasks.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class LocalLLMConfig:
    """Configuration for a local LLM."""
    name: str
    model_id: str
    size_gb: float
    ram_required_gb: float
    cpu_threads: int
    quantization: str
    context_length: int
    download_url: str
    strengths: List[str]
    use_case: str
    setup_commands: List[str]


# Recommended CPU-friendly models for Contabo VPS
# Assuming 4-8 CPU cores, 8-16GB RAM

RECOMMENDED_MODELS = {
    "phi4": LocalLLMConfig(
        name="Phi-4",
        model_id="microsoft/phi-4",
        size_gb=2.8,
        ram_required_gb=6.0,
        cpu_threads=4,
        quantization="Q4_K_M",
        context_length=16384,
        download_url="https://huggingface.co/microsoft/phi-4-gguf",
        strengths=[
            "excellent_reasoning",
            "fast_inference",
            "good_coding",
            "small_size",
            "high_quality_for_size"
        ],
        use_case="Primary reasoning and analysis tasks",
        setup_commands=[
            "# Install llama.cpp",
            "git clone https://github.com/ggerganov/llama.cpp.git",
            "cd llama.cpp && make -j4",
            "",
            "# Download Phi-4 GGUF",
            "wget https://huggingface.co/microsoft/phi-4-gguf/resolve/main/phi-4-Q4_K_M.gguf",
            "",
            "# Run server",
            "./llama-server -m phi-4-Q4_K_M.gguf -c 16384 --host 0.0.0.0 --port 8080"
        ]
    ),
    
    "qwen2.5_7b": LocalLLMConfig(
        name="Qwen2.5-7B-Instruct",
        model_id="Qwen/Qwen2.5-7B-Instruct-GGUF",
        size_gb=4.5,
        ram_required_gb=8.0,
        cpu_threads=4,
        quantization="Q4_K_M",
        context_length=32768,
        download_url="https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF",
        strengths=[
            "long_context",
            "multilingual",
            "good_coding",
            "fast",
            "reliable"
        ],
        use_case="Long context analysis and document processing",
        setup_commands=[
            "# Download Qwen2.5 GGUF",
            "wget https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf",
            "",
            "# Run server on different port",
            "./llama-server -m qwen2.5-7b-instruct-q4_k_m.gguf -c 32768 --host 0.0.0.0 --port 8081"
        ]
    ),
    
    "llama3.2_3b": LocalLLMConfig(
        name="Llama-3.2-3B-Instruct",
        model_id="bartowski/Llama-3.2-3B-Instruct-GGUF",
        size_gb=1.9,
        ram_required_gb=4.0,
        cpu_threads=2,
        quantization="Q4_K_M",
        context_length=128000,
        download_url="https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF",
        strengths=[
            "very_fast",
            "huge_context",
            "tool_use",
            "efficient",
            "good_quality"
        ],
        use_case="Quick replies and high-volume tasks",
        setup_commands=[
            "# Download Llama-3.2-3B GGUF",
            "wget https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "",
            "# Run server",
            "./llama-server -m Llama-3.2-3B-Instruct-Q4_K_M.gguf -c 32768 --host 0.0.0.0 --port 8082"
        ]
    ),
    
    "gemma2_4b": LocalLLMConfig(
        name="Gemma-2-4B-IT",
        model_id="bartowski/gemma-2-4b-it-GGUF",
        size_gb=2.6,
        ram_required_gb=5.0,
        cpu_threads=4,
        quantization="Q4_K_M",
        context_length=8192,
        download_url="https://huggingface.co/bartowski/gemma-2-4b-it-GGUF",
        strengths=[
            "google_quality",
            "good_reasoning",
            "fast",
            "reliable"
        ],
        use_case="Balanced tasks requiring Google-level quality",
        setup_commands=[
            "# Download Gemma-2 GGUF",
            "wget https://huggingface.co/bartowski/gemma-2-4b-it-GGUF/resolve/main/gemma-2-4b-it-Q4_K_M.gguf",
            "",
            "# Run server",
            "./llama-server -m gemma-2-4b-it-Q4_K_M.gguf -c 8192 --host 0.0.0.0 --port 8083"
        ]
    ),
    
    "deepseek_r1_7b": LocalLLMConfig(
        name="DeepSeek-R1-Distill-Qwen-7B",
        model_id="bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF",
        size_gb=4.5,
        ram_required_gb=8.0,
        cpu_threads=4,
        quantization="Q4_K_M",
        context_length=32768,
        download_url="https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF",
        strengths=[
            "excellent_reasoning",
            "chain_of_thought",
            "complex_analysis",
            "distilled_from_r1"
        ],
        use_case="Deep reasoning and complex investigation analysis",
        setup_commands=[
            "# Download DeepSeek-R1-Distill GGUF",
            "wget https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF/resolve/main/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
            "",
            "# Run server",
            "./llama-server -m DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf -c 32768 --host 0.0.0.0 --port 8084"
        ]
    )
}


# Recommended pairings for different server specs
SERVER_CONFIGS = {
    "minimal_4gb": {
        "description": "Minimal setup - 4GB RAM, 2 CPU cores",
        "models": ["llama3.2_3b"],
        "notes": "Single model only, will be slow but functional"
    },
    "standard_8gb": {
        "description": "Standard setup - 8GB RAM, 4 CPU cores",
        "models": ["phi4", "llama3.2_3b"],
        "notes": "Good balance of quality and speed"
    },
    "recommended_16gb": {
        "description": "Recommended setup - 16GB RAM, 6-8 CPU cores",
        "models": ["phi4", "qwen2.5_7b"],
        "notes": "Optimal for investigation tasks"
    },
    "premium_32gb": {
        "description": "Premium setup - 32GB RAM, 8+ CPU cores",
        "models": ["deepseek_r1_7b", "qwen2.5_7b", "llama3.2_3b"],
        "notes": "Can run multiple models simultaneously"
    }
}


# Task to model mapping
TASK_MODEL_MAPPING = {
    "quick_reply": {
        "primary": "llama3.2_3b",
        "fallback": "phi4",
        "reason": "Speed priority for Telegram responses"
    },
    "deep_analysis": {
        "primary": "phi4",
        "fallback": "deepseek_r1_7b",
        "reason": "Reasoning quality priority"
    },
    "long_context": {
        "primary": "qwen2.5_7b",
        "fallback": "llama3.2_3b",
        "reason": "Context length priority"
    },
    "coding": {
        "primary": "phi4",
        "fallback": "qwen2.5_7b",
        "reason": "Code generation quality"
    },
    "report_generation": {
        "primary": "deepseek_r1_7b",
        "fallback": "phi4",
        "reason": "Complex reasoning for reports"
    }
}


def get_model_config(model_name: str) -> Optional[LocalLLMConfig]:
    """Get configuration for a specific model."""
    return RECOMMENDED_MODELS.get(model_name)


def get_recommended_pairing(ram_gb: int = 8, cpu_cores: int = 4) -> List[str]:
    """
    Get recommended model pairing based on server specs.
    
    Args:
        ram_gb: Available RAM in GB
        cpu_cores: Number of CPU cores
        
    Returns:
        List of recommended model names
    """
    if ram_gb < 6:
        return SERVER_CONFIGS["minimal_4gb"]["models"]
    elif ram_gb < 12:
        return SERVER_CONFIGS["standard_8gb"]["models"]
    elif ram_gb < 24:
        return SERVER_CONFIGS["recommended_16gb"]["models"]
    else:
        return SERVER_CONFIGS["premium_32gb"]["models"]


def get_model_for_task(task_type: str, available_models: List[str] = None) -> str:
    """
    Get best model for a specific task.
    
    Args:
        task_type: Type of task (quick_reply, deep_analysis, etc.)
        available_models: List of available model names
        
    Returns:
        Recommended model name
    """
    mapping = TASK_MODEL_MAPPING.get(task_type, TASK_MODEL_MAPPING["deep_analysis"])
    
    if available_models:
        if mapping["primary"] in available_models:
            return mapping["primary"]
        if mapping["fallback"] in available_models:
            return mapping["fallback"]
    
    return mapping["primary"]


def generate_setup_script(ram_gb: int = 8, cpu_cores: int = 4) -> str:
    """
    Generate complete setup script for local LLMs.
    
    Args:
        ram_gb: Available RAM in GB
        cpu_cores: Number of CPU cores
        
    Returns:
        Bash script as string
    """
    models = get_recommended_pairing(ram_gb, cpu_cores)
    
    script = """#!/bin/bash
# RMI Local LLM Setup Script
# Generated for server specs: {}GB RAM, {} CPU cores
# 
# Run this script on your Contabo VPS to set up local LLMs

set -e

echo "🔧 Setting up local LLMs for RMI..."

# Create directory
mkdir -p ~/rmi-llms
cd ~/rmi-llms

# Install dependencies
echo "📦 Installing dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential git wget

# Clone and build llama.cpp
echo "🔨 Building llama.cpp..."
if [ ! -d "llama.cpp" ]; then
    git clone https://github.com/ggerganov/llama.cpp.git
fi
cd llama.cpp
make clean
make -j{cpu_cores}
cd ..

# Create model directory
mkdir -p models
cd models

""".format(ram_gb, cpu_cores, cpu_cores=cpu_cores)
    
    for model_name in models:
        config = RECOMMENDED_MODELS.get(model_name)
        if config:
            script += f"""
# Download {config.name}
echo "⬇️  Downloading {config.name}..."
if [ ! -f "{config.model_id.split('/')[-1]}-Q4_K_M.gguf" ]; then
    wget -O {config.model_id.split('/')[-1]}-Q4_K_M.gguf "{config.download_url}"
fi
"""
    
    script += """
# Create systemd service files
cd ~/rmi-llms

"""
    
    # Add service files for each model
    port = 8080
    for model_name in models:
        config = RECOMMENDED_MODELS.get(model_name)
        if config:
            model_file = f"{config.model_id.split('/')[-1]}-Q4_K_M.gguf"
            script += f"""# Service for {config.name}
cat > /tmp/rmi-llm-{port}.service << 'EOF'
[Unit]
Description=RMI Local LLM - {config.name}
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/rmi-llms/llama.cpp
ExecStart=/root/rmi-llms/llama.cpp/llama-server -m /root/rmi-llms/models/{model_file} -c {config.context_length} --host 0.0.0.0 --port {port}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/rmi-llm-{port}.service /etc/systemd/system/
sudo systemctl enable rmi-llm-{port}

"""
            port += 1
    
    script += f"""
# Start services
echo "🚀 Starting LLM services..."
"""
    
    port = 8080
    for _ in models:
        script += f"sudo systemctl start rmi-llm-{port}\n"
        port += 1
    
    script += f"""
echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Local LLM Endpoints:"
"""
    
    port = 8080
    for model_name in models:
        config = RECOMMENDED_MODELS.get(model_name)
        if config:
            script += f'echo "  • {config.name}: http://localhost:{port}"\n'
            port += 1
    
    script += """
echo ""
echo "📝 To check status:"
echo "  sudo systemctl status rmi-llm-<port>"
echo ""
echo "🔄 To restart:"
echo "  sudo systemctl restart rmi-llm-<port>"
echo ""
"""
    
    return script


def print_recommendations():
    """Print all recommendations."""
    print("=" * 70)
    print("CPU-FRIENDLY LOCAL LLM RECOMMENDATIONS")
    print("=" * 70)
    
    print("\n📊 TOP RECOMMENDATIONS FOR RMI:")
    print("\n1️⃣  Phi-4 (Microsoft)")
    print("   Size: 2.8GB | RAM: 6GB | Context: 16K")
    print("   Best for: Primary reasoning and analysis")
    print("   Why: Excellent quality for size, very fast inference")
    
    print("\n2️⃣  Qwen2.5-7B-Instruct (Alibaba)")
    print("   Size: 4.5GB | RAM: 8GB | Context: 32K")
    print("   Best for: Long context and document analysis")
    print("   Why: Huge context, reliable, good multilingual support")
    
    print("\n3️⃣  Llama-3.2-3B-Instruct (Meta)")
    print("   Size: 1.9GB | RAM: 4GB | Context: 128K")
    print("   Best for: Quick replies and high-volume tasks")
    print("   Why: Very fast, huge context, efficient")
    
    print("\n" + "-" * 70)
    print("\n🎯 RECOMMENDED PAIRING FOR 8GB RAM:")
    print("   Primary: Phi-4 (port 8080) - Deep analysis")
    print("   Secondary: Llama-3.2-3B (port 8081) - Quick replies")
    
    print("\n🎯 RECOMMENDED PAIRING FOR 16GB RAM:")
    print("   Primary: Phi-4 (port 8080) - General tasks")
    print("   Secondary: Qwen2.5-7B (port 8081) - Long context")
    print("   Tertiary: Llama-3.2-3B (port 8082) - Quick tasks")
    
    print("\n" + "-" * 70)
    print("\n⚡ TASK ASSIGNMENT:")
    for task, mapping in TASK_MODEL_MAPPING.items():
        print(f"   {task}: {mapping['primary']} ({mapping['reason']})")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print_recommendations()
    
    # Generate setup script
    print("\n📝 Generating setup script for 8GB RAM server...")
    script = generate_setup_script(ram_gb=8, cpu_cores=4)
    
    script_path = "/mnt/okcomputer/output/omega_forensic_v5/setup_local_llms.sh"
    with open(script_path, 'w') as f:
        f.write(script)
    
    print(f"✅ Setup script saved to: {script_path}")
    print("\nTo use:")
    print(f"  chmod +x {script_path}")
    print(f"  ./{script_path}")
