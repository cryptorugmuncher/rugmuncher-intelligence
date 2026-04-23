"""
Swarm Railway Training Data Sync
Integrates AI Swarm with Railway-hosted training data collector
"""

import os
import json
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass
import aiohttp
import hashlib
from datetime import datetime

RAILWAY_URL = os.getenv("RAILWAY_TRAINING_URL", "https://your-app.railway.app")
API_KEY = os.getenv("RAILWAY_TRAINING_API_KEY", "swarm-train-2024")

@dataclass
class TrainingBatch:
    batch_id: str
    samples: List[Dict]
    category: str
    fetched_at: datetime

class RailwayTrainingClient:
    """Client to sync training data from Railway service"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or RAILWAY_URL
        self.api_key = api_key or API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict:
        """Check if Railway service is healthy"""
        async with self.session.get(f"{self.base_url}/health") as resp:
            return await resp.json()
    
    async def get_stats(self) -> Dict:
        """Get training data statistics"""
        async with self.session.get(f"{self.base_url}/stats") as resp:
            return await resp.json()
    
    async def fetch_training_batch(
        self,
        bot_id: str,
        categories: List[str] = None,
        difficulty_min: int = 1,
        difficulty_max: int = 5,
        count: int = 10,
        exclude_ids: List[str] = None
    ) -> TrainingBatch:
        """Fetch a batch of training samples for a bot"""
        
        payload = {
            "bot_id": bot_id,
            "categories": categories or [],
            "difficulty_min": difficulty_min,
            "difficulty_max": difficulty_max,
            "count": count,
            "exclude_ids": exclude_ids or []
        }
        
        async with self.session.post(
            f"{self.base_url}/training/batch",
            json=payload
        ) as resp:
            data = await resp.json()
            
            return TrainingBatch(
                batch_id=data["batch_id"],
                samples=data["samples"],
                category=categories[0] if categories else "mixed",
                fetched_at=datetime.fromisoformat(data["fetched_at"])
            )
    
    async def submit_feedback(
        self,
        sample_id: str,
        bot_id: str,
        accuracy: float
    ) -> Dict:
        """Submit accuracy feedback for a sample"""
        payload = {
            "sample_id": sample_id,
            "bot_id": bot_id,
            "accuracy": accuracy
        }
        
        async with self.session.post(
            f"{self.base_url}/training/feedback",
            json=payload
        ) as resp:
            return await resp.json()
    
    async def get_categories(self) -> Dict:
        """Get available training categories"""
        async with self.session.get(f"{self.base_url}/training/categories") as resp:
            return await resp.json()


class SwarmRailwayIntegration:
    """
    Bridge between AI Swarm and Railway training data
    Allows swarm bots to train on data hosted on Railway
    """
    
    def __init__(self, swarm_orchestrator, railway_url: str = None):
        self.swarm = swarm_orchestrator
        self.railway_url = railway_url or RAILWAY_URL
        self.synced_samples: Dict[str, List[str]] = {}  # bot_id -> sample_ids
        
    async def sync_training_data(
        self,
        bot_ids: Optional[List[str]] = None,
        categories: List[str] = None,
        samples_per_bot: int = 10
    ) -> Dict:
        """
        Sync training data from Railway to swarm bots
        """
        if not bot_ids:
            bot_ids = list(self.swarm.bots.keys()) if hasattr(self.swarm, 'bots') else []
        
        if not bot_ids:
            return {"error": "No bots available for training"}
        
        results = []
        
        async with RailwayTrainingClient(self.railway_url) as client:
            # Check health first
            health = await client.health_check()
            print(f"📡 Railway training service: {health['samples_available']} samples available")
            
            for bot_id in bot_ids:
                # Determine difficulty based on bot performance (if available)
                difficulty_min, difficulty_max = self._get_difficulty_range(bot_id)
                
                # Fetch batch
                exclude_ids = self.synced_samples.get(bot_id, [])
                
                try:
                    batch = await client.fetch_training_batch(
                        bot_id=bot_id,
                        categories=categories,
                        difficulty_min=difficulty_min,
                        difficulty_max=difficulty_max,
                        count=samples_per_bot,
                        exclude_ids=exclude_ids
                    )
                    
                    # Convert to swarm training tasks
                    tasks = self._convert_to_training_tasks(batch, bot_id)
                    
                    # Track synced samples
                    new_ids = [s["id"] for s in batch.samples]
                    self.synced_samples[bot_id] = exclude_ids + new_ids
                    
                    results.append({
                        "bot_id": bot_id,
                        "batch_id": batch.batch_id,
                        "samples_fetched": len(batch.samples),
                        "difficulty_range": f"{difficulty_min}-{difficulty_max}",
                        "tasks_created": len(tasks),
                        "status": "success"
                    })
                    
                    print(f"✅ {bot_id}: Fetched {len(batch.samples)} samples (difficulty {difficulty_min}-{difficulty_max})")
                    
                except Exception as e:
                    print(f"❌ {bot_id}: Failed to fetch - {e}")
                    results.append({
                        "bot_id": bot_id,
                        "error": str(e),
                        "status": "failed"
                    })
        
        return {
            "sync_id": hashlib.sha256(datetime.now().isoformat().encode()).hexdigest()[:16],
            "railway_url": self.railway_url,
            "bots_synced": len([r for r in results if r.get("status") == "success"]),
            "total_samples": sum(r.get("samples_fetched", 0) for r in results),
            "results": results
        }
    
    def _get_difficulty_range(self, bot_id: str) -> tuple:
        """Determine appropriate difficulty based on bot capabilities"""
        # Simple heuristic based on bot name
        bot_lower = bot_id.lower()
        
        if "mistral" in bot_lower or "qwen" in bot_lower or "480b" in bot_lower:
            return (3, 5)  # Advanced models get harder tasks
        elif "deepseek" in bot_lower or "claude" in bot_lower:
            return (2, 4)  # Analysis models get medium-hard
        else:
            return (1, 3)  # Others get beginner-intermediate
    
    def _convert_to_training_tasks(self, batch: TrainingBatch, bot_id: str) -> List[Dict]:
        """Convert Railway samples to swarm training tasks"""
        tasks = []
        
        for sample in batch.samples:
            task = {
                "task_id": f"railway_{sample['id']}",
                "bot_id": bot_id,
                "type": "training",
                "category": sample["category"],
                "difficulty": sample["difficulty"],
                "content": sample["content"],
                "expected_output": sample.get("expected_output"),
                "source": "railway",
                "batch_id": batch.batch_id,
                "original_sample_id": sample["id"]
            }
            tasks.append(task)
        
        return tasks
    
    async def submit_training_results(
        self,
        results: List[Dict]
    ) -> Dict:
        """
        Submit training results back to Railway for feedback loop
        """
        feedback_count = 0
        
        async with RailwayTrainingClient(self.railway_url) as client:
            for result in results:
                if "original_sample_id" in result and "accuracy" in result:
                    try:
                        await client.submit_feedback(
                            sample_id=result["original_sample_id"],
                            bot_id=result["bot_id"],
                            accuracy=result["accuracy"]
                        )
                        feedback_count += 1
                    except Exception as e:
                        print(f"Failed to submit feedback: {e}")
        
        return {
            "feedback_submitted": feedback_count,
            "status": "completed"
        }


# CLI command integration for launch_swarm.py
RAILWAY_SYNC_COMMANDS = """
# Add these commands to launch_swarm.py interactive_mode:

elif cmd == "railway_sync":
    print("\\n📡 SYNCING TRAINING DATA FROM RAILWAY")
    print("=" * 50)
    
    from swarm_railway_sync import SwarmRailwayIntegration
    
    # Parse args
    category = args[1] if len(args) > 1 else None
    count = int(args[2]) if len(args) > 2 else 10
    
    # Get Railway URL
    railway_url = os.getenv("RAILWAY_TRAINING_URL")
    if not railway_url:
        railway_url = input("Railway training service URL: ").strip()
    
    integration = SwarmRailwayIntegration(swarm, railway_url)
    
    categories = [category] if category else None
    
    result = await integration.sync_training_data(
        categories=categories,
        samples_per_bot=count
    )
    
    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        print(f"\\n✅ Sync Complete: {result['sync_id']}")
        print(f"   Railway: {result['railway_url']}")
        print(f"   Bots synced: {result['bots_synced']}")
        print(f"   Total samples: {result['total_samples']}")
        print("\\nBreakdown:")
        for r in result['results']:
            if r['status'] == 'success':
                print(f"   ✓ {r['bot_id']}: {r['samples_fetched']} samples ({r['difficulty_range']})")
            else:
                print(f"   ✗ {r['bot_id']}: {r.get('error', 'Failed')}")

elif cmd == "railway_stats":
    from swarm_railway_sync import RailwayTrainingClient
    
    railway_url = os.getenv("RAILWAY_TRAINING_URL")
    if not railway_url:
        railway_url = input("Railway URL: ").strip()
    
    async with RailwayTrainingClient(railway_url) as client:
        health = await client.health_check()
        stats = await client.get_stats()
        categories = await client.get_categories()
    
    print("\\n📊 RAILWAY TRAINING SERVICE STATUS")
    print("=" * 50)
    print(f"Status: {health['status']}")
    print(f"Samples: {health['samples_available']}")
    print(f"Last updated: {health['timestamp']}")
    
    print("\\n📈 Statistics:")
    for cat, levels in stats.get('by_category', {}).items():
        total = sum(levels.values())
        print(f"   {cat}: {total} samples")
        for level, count in levels.items():
            print(f"      {level}: {count}")
    
    print(f"\\n🔄 Recent activity (24h):")
    print(f"   Syncs: {stats.get('recent_syncs_24h', 0)}")
    print(f"   Samples fetched: {stats.get('samples_fetched_24h', 0)}")

elif cmd == "railway_seed":
    print("\\n🌱 SEEDING LOCAL TRAINING DATA")
    print("=" * 50)
    
    # Run the local collector to seed data
    from railway_training_collector import CryptoScamCollector, WalletForensicsCollector, init_db, get_db
    import json
    
    init_db()
    
    crypto_cases = CryptoScamCollector.generate_synthetic_cases(100)
    wallet_profiles = WalletForensicsCollector.generate_profiles(50)
    
    conn = get_db()
    cursor = conn.cursor()
    
    inserted = 0
    for case in crypto_cases + wallet_profiles:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO training_samples 
                (id, category, difficulty, content, expected_output, metadata, source, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case["id"],
                case["category"],
                case["difficulty"],
                json.dumps(case["content"]),
                json.dumps(case.get("expected_output")),
                json.dumps(case.get("metadata", {})),
                "local_seed",
                json.dumps(case.get("tags", []))
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"Skip {case['id']}: {e}")
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM training_samples")
    total = cursor.fetchone()[0]
    conn.close()
    
    print(f"✅ Inserted {inserted} new samples")
    print(f"📦 Total in local DB: {total}")
"""


if __name__ == "__main__":
    # Demo/test the Railway integration
    import asyncio
    
    async def test():
        print("🧪 Testing Railway Training Client")
        print("=" * 50)
        
        # Test with local server (if running)
        client = RailwayTrainingClient("http://localhost:8000")
        
        try:
            async with client:
                health = await client.health_check()
                print(f"✅ Health check: {health['samples_available']} samples")
                
                stats = await client.get_stats()
                print(f"📊 Stats: {stats}")
                
                batch = await client.fetch_training_batch(
                    bot_id="test_bot_qwen3",
                    categories=["crypto_scam"],
                    count=3
                )
                print(f"📦 Batch: {batch.batch_id}")
                print(f"   Samples: {len(batch.samples)}")
                
                for s in batch.samples[:2]:
                    print(f"\n   Sample: {s['id']}")
                    print(f"   Category: {s['category']}, Difficulty: {s['difficulty']}")
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("Make sure the Railway collector is running: python railway_training_collector.py")
    
    asyncio.run(test())
