#!/usr/bin/env python3
"""
RMI DexScreener Scam Finder — Original Detection Engine
=======================================================
Multi-signal scam detection using DexScreener free API.

Original Features:
- Profile Flip Detector: Tokens rebranding after rugs
- Boost Trap Analyzer: Promoted tokens with declining metrics  
- CTA Risk Scorer: Community takeovers with insider risk
- Meta Scam Hunter: Hype-riding tokens without substance
- Fresh Pair Scanner: New pairs with suspicious volume
- Description Similarity: Clone/bot-created tokens
"""

import asyncio
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from difflib import SequenceMatcher

BASE_URL = "https://api.dexscreener.com"

class DexScreenerScamFinder:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self._cache = {}
        self._last_call = 0
    
    async def _call(self, endpoint: str, params: dict = None) -> dict:
        import time
        now = time.time()
        wait = 1.1 - (now - self._last_call)  # 60 RPM = 1 req/sec safe
        if wait > 0: await asyncio.sleep(wait)
        self._last_call = time.time()
        try:
            r = await self.client.get(f"{BASE_URL}{endpoint}", params=params or {}, timeout=15)
            return r.json() if r.status_code == 200 else {"error": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # CORE DATA FETCHING
    # ═══════════════════════════════════════════════════════════════
    
    async def get_token_profiles_latest(self) -> List[Dict]:
        r = await self._call("/token-profiles/latest/v1")
        return r if isinstance(r, list) else []
    
    async def get_token_profiles_recent_updates(self) -> List[Dict]:
        r = await self._call("/token-profiles/recent-updates/v1")
        return r if isinstance(r, list) else []
    
    async def get_community_takeovers(self) -> List[Dict]:
        r = await self._call("/community-takeovers/latest/v1")
        return r if isinstance(r, list) else []
    
    async def get_token_boosts_latest(self) -> List[Dict]:
        r = await self._call("/token-boosts/latest/v1")
        return r if isinstance(r, list) else []
    
    async def get_token_boosts_top(self) -> List[Dict]:
        r = await self._call("/token-boosts/top/v1")
        return r if isinstance(r, list) else []
    
    async def get_trending_metas(self) -> List[Dict]:
        r = await self._call("/metas/trending/v1")
        return r if isinstance(r, list) else []
    
    async def search_pairs(self, query: str) -> List[Dict]:
        r = await self._call("/latest/dex/search", {"q": query})
        return r.get("pairs", []) if isinstance(r, dict) else []
    
    async def get_pair_details(self, chain_id: str, pair_id: str) -> Dict:
        r = await self._call(f"/latest/dex/pairs/{chain_id}/{pair_id}")
        return r if isinstance(r, dict) else {}
    
    async def get_token_pairs(self, chain_id: str, token_address: str) -> Dict:
        r = await self._call(f"/token-pairs/v1/{chain_id}/{token_address}")
        return r if isinstance(r, dict) else {}
    
    # ═══════════════════════════════════════════════════════════════
    # ORIGINAL FEATURES
    # ═══════════════════════════════════════════════════════════════
    
    async def profile_flip_detector(self) -> Dict:
        """
        ORIGINAL #1: Profile Flip Detector
        Tokens that recently updated their profile may be rebranding after a rug.
        Compares latest profiles vs recent updates to find suspicious flips.
        """
        latest = await self.get_token_profiles_latest()
        await asyncio.sleep(1.2)
        recent_updates = await self.get_token_profiles_recent_updates()
        
        # Find tokens in both lists (recently updated AND in latest)
        latest_addrs = {p.get("tokenAddress", ""): p for p in latest}
        flips = []
        
        for updated in recent_updates:
            addr = updated.get("tokenAddress", "")
            if addr in latest_addrs:
                original = latest_addrs[addr]
                
                # Detect changes
                changes = []
                
                # Description changed
                old_desc = (original.get("description") or "").lower()
                new_desc = (updated.get("description") or "").lower()
                if old_desc and new_desc and old_desc != new_desc:
                    similarity = SequenceMatcher(None, old_desc, new_desc).ratio()
                    if similarity < 0.7:
                        changes.append(f"Description completely rewritten ({similarity:.0%} similar)")
                
                # Links changed
                old_links = {l.get("url", "") for l in (original.get("links") or [])}
                new_links = {l.get("url", "") for l in (updated.get("links") or [])}
                removed = old_links - new_links
                added = new_links - old_links
                if removed: changes.append(f"Removed {len(removed)} social links")
                if added: changes.append(f"Added {len(added)} new social links")
                
                # Icon/header changed
                if original.get("icon") != updated.get("icon"):
                    changes.append("Token icon changed")
                if original.get("header") != updated.get("header"):
                    changes.append("Banner/header image changed")
                
                if len(changes) >= 2:
                    flips.append({
                        "token_address": addr,
                        "chain_id": updated.get("chainId", ""),
                        "url": updated.get("url", ""),
                        "changes": changes,
                        "flip_score": len(changes) * 15 + (5 if removed else 0),
                        "old_description": original.get("description", "")[:100],
                        "new_description": updated.get("description", "")[:100],
                    })
        
        # Score and rank
        flips.sort(key=lambda x: x["flip_score"], reverse=True)
        
        high_risk = [f for f in flips if f["flip_score"] >= 40]
        
        return {
            "scan_type": "profile_flip_detector",
            "tokens_scanned": len(latest_addrs),
            "flips_detected": len(flips),
            "high_risk_flips": len(high_risk),
            "flips": flips[:20],
            "verdict": f"🚨 {len(high_risk)} HIGH RISK profile flips detected" if high_risk else f"🟢 {len(flips)} minor profile changes found",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def boost_trap_analyzer(self) -> Dict:
        """
        ORIGINAL #2: Boost Trap Analyzer
        Tokens paying for promotion (boosts) but showing declining metrics.
        Classic exit liquidity trap pattern.
        """
        boosts = await self.get_token_boosts_latest()
        await asyncio.sleep(1.2)
        top_boosts = await self.get_token_boosts_top()
        
        all_boosted = {b.get("tokenAddress", ""): b for b in boosts + top_boosts}
        traps = []
        
        for addr, boost in all_boosted.items():
            # Get pair data for this token
            pairs = await self.search_pairs(addr)
            await asyncio.sleep(1.2)
            
            if not pairs: continue
            
            pair = pairs[0]
            
            # Analyze metrics
            vol_24h = pair.get("volume", {}).get("h24", 0)
            vol_6h = pair.get("volume", {}).get("h6", 0)
            price_chg = pair.get("priceChange", {})
            txns = pair.get("txns", {})
            
            # Red flags
            flags = []
            trap_score = 0
            
            # Declining volume: 6h should be ~25% of 24h if steady
            if vol_24h > 0 and vol_6h < vol_24h * 0.1:
                flags.append("Volume collapsed — 6h is less than 10% of 24h")
                trap_score += 25
            
            # Declining price despite boost
            h1_chg = price_chg.get("h1", 0)
            h6_chg = price_chg.get("h6", 0)
            if h1_chg < -10 and h6_chg < -20:
                flags.append(f"Price dropping {h6_chg:.1f}% in 6h despite paid promotion")
                trap_score += 25
            
            # More sells than buys
            h24_txns = txns.get("h24", {})
            buys = h24_txns.get("buys", 0)
            sells = h24_txns.get("sells", 0)
            if sells > buys * 1.5:
                flags.append(f"Sell pressure: {sells} sells vs {buys} buys (24h)")
                trap_score += 20
            
            # Very low liquidity
            liq = pair.get("liquidity", {}).get("usd", 0)
            if liq < 10000:
                flags.append(f"Low liquidity: ${liq:,.0f}")
                trap_score += 15
            
            # Boost but no holders
            fdv = pair.get("fdv", 0)
            mcap = pair.get("marketCap", 0)
            if mcap > 0 and vol_24h > mcap * 3:
                flags.append("Volume 3x+ market cap — wash trading with boost")
                trap_score += 20
            
            if trap_score >= 30:
                traps.append({
                    "token_address": addr,
                    "chain_id": pair.get("chainId", ""),
                    "symbol": pair.get("baseToken", {}).get("symbol", "???"),
                    "name": pair.get("baseToken", {}).get("name", "???"),
                    "trap_score": min(trap_score, 100),
                    "flags": flags,
                    "price_change_1h": h1_chg,
                    "price_change_6h": h6_chg,
                    "volume_24h": vol_24h,
                    "liquidity": liq,
                    "market_cap": mcap,
                })
        
        traps.sort(key=lambda x: x["trap_score"], reverse=True)
        
        return {
            "scan_type": "boost_trap_analyzer",
            "boosted_tokens_analyzed": len(all_boosted),
            "traps_detected": len(traps),
            "high_risk_traps": len([t for t in traps if t["trap_score"] >= 60]),
            "traps": traps[:15],
            "verdict": f"🚨 {len(traps)} boost traps detected" if traps else "🟢 No boost traps found",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def cta_risk_scorer(self) -> Dict:
        """
        ORIGINAL #3: Community Takeover Risk Scorer
        CTAs often follow rugs where insiders abandoned.
        Scores risk based on takeover quality.
        """
        ctas = await self.get_community_takeovers()
        
        scored = []
        for cta in ctas:
            addr = cta.get("tokenAddress", "")
            chain = cta.get("chainId", "")
            
            # Get pair data
            pairs_data = await self.get_token_pairs(chain, addr)
            await asyncio.sleep(1.2)
            
            pairs = pairs_data.get("pairs", []) if isinstance(pairs_data, dict) else []
            
            risk_score = 0
            flags = []
            signals = []
            
            # Check if CTA has proper setup
            desc = (cta.get("description") or "").lower()
            links = cta.get("links") or []
            
            if not desc:
                risk_score += 15; flags.append("No CTA description — low effort")
            elif len(desc) < 50:
                risk_score += 10; flags.append("Very short CTA description")
            else:
                signals.append("Detailed CTA plan")
            
            if len(links) < 2:
                risk_score += 15; flags.append("Few social links — limited community infrastructure")
            else:
                signals.append(f"{len(links)} social links set up")
            
            # Check pair health
            if pairs:
                best_pair = max(pairs, key=lambda p: p.get("liquidity", {}).get("usd", 0) or 0)
                liq = best_pair.get("liquidity", {}).get("usd", 0)
                vol_24h = best_pair.get("volume", {}).get("h24", 0)
                mcap = best_pair.get("marketCap", 0) or best_pair.get("fdv", 0)
                
                if liq < 5000: risk_score += 20; flags.append(f"Very low liquidity: ${liq:,.0f}")
                elif liq < 20000: risk_score += 10; flags.append(f"Low liquidity: ${liq:,.0f}")
                else: signals.append(f"Good liquidity: ${liq:,.0f}")
                
                if mcap > 0 and vol_24h > mcap * 5:
                    risk_score += 15; flags.append("Suspicious volume vs market cap")
                
                holder_count = best_pair.get("holderCount", 0)
                if holder_count and holder_count < 100:
                    risk_score += 10; flags.append(f"Only {holder_count} holders")
            else:
                risk_score += 25; flags.append("No trading pairs found")
            
            # CTA age (if available)
            claim_date = cta.get("claimDate", "")
            if claim_date:
                try:
                    claimed = datetime.fromisoformat(claim_date.replace("Z", "+00:00"))
                    hours_since = (datetime.utcnow() - claimed.replace(tzinfo=None)).total_seconds() / 3600
                    if hours_since < 24: risk_score += 5; flags.append("CTA less than 24h old")
                    elif hours_since > 168: signals.append("CTA established for over a week")
                except: pass
            
            if risk_score >= 50: level = "🔴 HIGH RISK CTA"
            elif risk_score >= 30: level = "🟡 MODERATE RISK"
            elif risk_score >= 15: level = "🟢 LOW-MODERATE RISK"
            else: level = "🟢 HEALTHY CTA"
            
            scored.append({
                "token_address": addr,
                "chain_id": chain,
                "name": cta.get("baseToken", {}).get("name", "???"),
                "symbol": cta.get("baseToken", {}).get("symbol", "???"),
                "risk_score": min(risk_score, 100),
                "risk_level": level,
                "flags": flags,
                "positive_signals": signals,
                "claim_date": claim_date,
                "url": cta.get("url", ""),
            })
        
        scored.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return {
            "scan_type": "cta_risk_scorer",
            "ctas_analyzed": len(ctas),
            "high_risk": len([s for s in scored if s["risk_score"] >= 50]),
            "results": scored[:15],
            "verdict": f"🔴 {len([s for s in scored if s[risk_score] >= 50])} high-risk CTAs" if any(s["risk_score"] >= 50 for s in scored) else f"🟢 {len(scored)} CTAs analyzed",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def meta_scam_hunter(self) -> Dict:
        """
        ORIGINAL #4: Meta Scam Hunter
        Finds tokens riding trending narratives without substance.
        Cross-references trending metas with actual token quality.
        """
        metas = await self.get_trending_metas()
        
        meta_scams = []
        for meta in metas:
            slug = meta.get("slug", "")
            name = meta.get("name", "???")
            
            # Get full meta details
            details = await self._call(f"/metas/meta/v1/{slug}")
            await asyncio.sleep(1.2)
            
            pairs = details.get("pairs", []) if isinstance(details, dict) else []
            
            # Analyze tokens in this meta
            scam_tokens = []
            for pair in pairs[:10]:  # Top 10 tokens in meta
                flags = []
                hype_score = 0
                
                # Token with no socials riding meta
                info = pair.get("info", {})
                socials = info.get("socials", []) or []
                websites = info.get("websites", []) or []
                
                if not socials and not websites:
                    flags.append("No socials or website — pure meta rider")
                    hype_score += 30
                elif not websites:
                    flags.append("No website — Twitter-only meta play")
                    hype_score += 15
                
                # Very low liquidity but trending
                liq = pair.get("liquidity", {}).get("usd", 0)
                if liq and liq < 5000:
                    flags.append(f"Low liquidity ${liq:,.0f} but trending in meta")
                    hype_score += 20
                
                # Check if price is already dumped
                chg_24h = pair.get("priceChange", {}).get("h24", 0)
                if chg_24h and chg_24h < -50:
                    flags.append(f"Already dumped {chg_24h:.0f}% — late to the meta")
                    hype_score += 15
                
                if hype_score >= 30:
                    scam_tokens.append({
                        "address": pair.get("baseToken", {}).get("address", ""),
                        "symbol": pair.get("baseToken", {}).get("symbol", "???"),
                        "hype_score": hype_score,
                        "flags": flags,
                        "price_change_24h": chg_24h,
                        "liquidity": liq,
                    })
            
            if scam_tokens:
                meta_scams.append({
                    "meta_slug": slug,
                    "meta_name": name,
                    "meta_market_cap": meta.get("marketCap", 0),
                    "scam_tokens_found": len(scam_tokens),
                    "tokens": scam_tokens,
                })
        
        return {
            "scan_type": "meta_scam_hunter",
            "metas_analyzed": len(metas),
            "metas_with_scams": len(meta_scams),
            "total_scam_tokens": sum(m["scam_tokens_found"] for m in meta_scams),
            "results": meta_scams[:10],
            "verdict": f"🚨 Found scam tokens in {len(meta_scams)} trending metas" if meta_scams else "🟢 No meta scams detected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def fresh_pair_scanner(self) -> Dict:
        """
        ORIGINAL #5: Fresh Pair Scanner
        New pairs with suspicious volume patterns indicating manipulation.
        """
        # Search for recently created pairs
        pairs = await self.search_pairs("solana")
        await asyncio.sleep(1.2)
        
        fresh = []
        for pair in pairs[:50]:  # Check top 50
            created = pair.get("pairCreatedAt", 0)
            if not created: continue
            
            age_hours = (datetime.utcnow().timestamp() - (created / 1000)) / 3600
            if age_hours > 48: continue  # Only < 48h old
            
            flags = []
            suspicious_score = 0
            
            # Very new but high volume
            vol_1h = pair.get("volume", {}).get("h1", 0)
            vol_24h = pair.get("volume", {}).get("h24", 0)
            liq = pair.get("liquidity", {}).get("usd", 0)
            mcap = pair.get("marketCap", 0) or pair.get("fdv", 0)
            
            if vol_1h > 50000 and age_hours < 6:
                flags.append(f"${vol_1h/1e3:.0f}K volume in first {age_hours:.1f} hours")
                suspicious_score += 25
            
            if liq > 0 and vol_24h > liq * 3:
                flags.append(f"Volume {vol_24h/liq:.1f}x liquidity — wash trading")
                suspicious_score += 25
            
            # Price manipulation: huge jump then flat
            chg_m5 = pair.get("priceChange", {}).get("m5", 0)
            chg_1h = pair.get("priceChange", {}).get("h1", 0)
            if chg_m5 and chg_m5 > 50:
                flags.append(f"+{chg_m5:.0f}% in 5 minutes — manipulation pump")
                suspicious_score += 20
            
            # Low holder count
            txns = pair.get("txns", {})
            h24_buys = txns.get("h24", {}).get("buys", 0)
            h24_sells = txns.get("h24", {}).get("sells", 0)
            if h24_buys and h24_sells and h24_buys < 20:
                flags.append(f"Only {h24_buys} buy transactions — thin market")
                suspicious_score += 15
            
            if h24_sells > h24_buys * 2:
                flags.append("More sells than buys — dump in progress")
                suspicious_score += 15
            
            if suspicious_score >= 30:
                fresh.append({
                    "pair_address": pair.get("pairAddress", ""),
                    "dex": pair.get("dexId", ""),
                    "token_address": pair.get("baseToken", {}).get("address", ""),
                    "symbol": pair.get("baseToken", {}).get("symbol", "???"),
                    "age_hours": round(age_hours, 1),
                    "suspicious_score": min(suspicious_score, 100),
                    "flags": flags,
                    "price_change_1h": chg_1h,
                    "volume_24h": vol_24h,
                    "liquidity": liq,
                    "market_cap": mcap,
                })
        
        fresh.sort(key=lambda x: x["suspicious_score"], reverse=True)
        
        return {
            "scan_type": "fresh_pair_scanner",
            "pairs_analyzed": len(pairs),
            "fresh_pairs": len(fresh),
            "high_risk": len([f for f in fresh if f["suspicious_score"] >= 60]),
            "pairs": fresh[:15],
            "verdict": f"🚨 {len(fresh)} suspicious fresh pairs" if fresh else "🟢 No suspicious fresh pairs",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def clone_detector(self) -> Dict:
        """
        ORIGINAL #6: Clone/Copycat Detector
        Compares token descriptions across latest profiles to find
        copy-paste/bot-created tokens.
        """
        profiles = await self.get_token_profiles_latest()
        
        clones = []
        checked = set()
        
        for i, p1 in enumerate(profiles):
            addr1 = p1.get("tokenAddress", "")
            if addr1 in checked: continue
            
            desc1 = (p1.get("description") or "").lower().strip()
            if len(desc1) < 20: continue  # Skip empty/short descriptions
            
            matches = []
            for j, p2 in enumerate(profiles):
                if i == j: continue
                addr2 = p2.get("tokenAddress", "")
                if addr2 in checked: continue
                
                desc2 = (p2.get("description") or "").lower().strip()
                if len(desc2) < 20: continue
                
                similarity = SequenceMatcher(None, desc1, desc2).ratio()
                
                if similarity > 0.7:  # 70% similar
                    matches.append({
                        "token_address": addr2,
                        "symbol": p2.get("symbol", "???"),
                        "similarity": round(similarity * 100, 1),
                        "description_preview": desc2[:80],
                    })
                    checked.add(addr2)
            
            if matches:
                clones.append({
                    "original_address": addr1,
                    "original_symbol": p1.get("symbol", "???"),
                    "original_description": desc1[:100],
                    "clones_found": len(matches),
                    "matches": matches,
                    "highest_similarity": max(m["similarity"] for m in matches),
                })
                checked.add(addr1)
        
        clones.sort(key=lambda x: x["highest_similarity"], reverse=True)
        
        high_confidence = [c for c in clones if c["highest_similarity"] >= 85]
        
        return {
            "scan_type": "clone_detector",
            "profiles_analyzed": len(profiles),
            "clone_groups_found": len(clones),
            "high_confidence_clones": len(high_confidence),
            "clones": clones[:15],
            "verdict": f"🚨 {len(high_confidence)} high-confidence clone groups" if high_confidence else f"🟡 {len(clones)} potential copycats found",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def full_scam_scan(self) -> Dict:
        """
        ULTIMATE: Run ALL scam detectors and compile report.
        """
        results = await asyncio.gather(
            self.profile_flip_detector(),
            self.boost_trap_analyzer(),
            self.cta_risk_scorer(),
            self.meta_scam_hunter(),
            self.fresh_pair_scanner(),
            self.clone_detector(),
            return_exceptions=True,
        )
        
        scans = {
            "profile_flips": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "boost_traps": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "cta_risks": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
            "meta_scams": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])},
            "fresh_pairs": results[4] if not isinstance(results[4], Exception) else {"error": str(results[4])},
            "clones": results[5] if not isinstance(results[5], Exception) else {"error": str(results[5])},
        }
        
        # Calculate total threats
        total_threats = sum([
            scans["profile_flips"].get("high_risk_flips", 0),
            scans["boost_traps"].get("traps_detected", 0),
            scans["cta_risks"].get("high_risk", 0),
            scans["meta_scams"].get("total_scam_tokens", 0),
            scans["fresh_pairs"].get("high_risk", 0),
            scans["clones"].get("high_confidence_clones", 0),
        ])
        
        if total_threats >= 20: overall = "🔴 CRITICAL — Widespread scam activity"
        elif total_threats >= 10: overall = "🟠 HIGH — Multiple active threats"
        elif total_threats >= 5: overall = "🟡 MODERATE — Some threats detected"
        elif total_threats > 0: overall = "🟢 LOW — Minor concerns"
        else: overall = "✅ CLEAN — No scams detected"
        
        return {
            "overall_verdict": overall,
            "total_threats": total_threats,
            "scans": scans,
            "scanned_at": datetime.utcnow().isoformat(),
            "source": "dexscreener_scam_finder",
            "features": [
                "profile_flip_detector",
                "boost_trap_analyzer",
                "cta_risk_scorer",
                "meta_scam_hunter",
                "fresh_pair_scanner",
                "clone_detector",
            ],
        }
    
    async def close(self):
        await self.client.aclose()
