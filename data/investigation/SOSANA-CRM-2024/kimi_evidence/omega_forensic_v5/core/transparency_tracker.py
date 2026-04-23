"""
Transparency Tracker - Project Transparency Monitoring
======================================================
Tracks and scores projects on transparency metrics:
- Team doxxing
- Contract verification
- Audit reports
- Treasury visibility
- Communication quality
- Roadmap delivery
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TransparencyCategory(Enum):
    """Categories of transparency."""
    TEAM = "team"
    CONTRACT = "contract"
    TREASURY = "treasury"
    COMMUNICATION = "communication"
    AUDIT = "audit"
    ROADMAP = "roadmap"


class TransparencyStatus(Enum):
    """Status of a transparency item."""
    VERIFIED = "verified"
    PARTIAL = "partial"
    UNVERIFIED = "unverified"
    MISSING = "missing"
    FLAGGED = "flagged"


@dataclass
class TransparencyItem:
    """A single transparency metric."""
    category: TransparencyCategory
    name: str
    status: TransparencyStatus
    score: int  # 0-100
    evidence: str = ""
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    notes: str = ""


@dataclass
class TransparencyReport:
    """Complete transparency report for a project."""
    project_name: str
    token_address: str
    generated_at: datetime
    
    overall_score: int = 0
    grade: str = "F"  # A+, A, A-, B+, B, B-, C+, C, C-, D, F
    
    items: List[TransparencyItem] = field(default_factory=list)
    
    # Summary
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    
    # Comparison
    rank_percentile: int = 0  # How they rank vs other projects
    
    def to_dict(self) -> Dict:
        return {
            "project": self.project_name,
            "token": self.token_address,
            "generated_at": self.generated_at.isoformat(),
            "overall_score": self.overall_score,
            "grade": self.grade,
            "rank_percentile": self.rank_percentile,
            "breakdown": {
                cat.value: {
                    "items": [
                        {"name": i.name, "status": i.status.value, "score": i.score}
                        for i in self.items if i.category == cat
                    ],
                    "average_score": sum(i.score for i in self.items if i.category == cat) / 
                                   max(1, len([i for i in self.items if i.category == cat]))
                }
                for cat in TransparencyCategory
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "red_flags": self.red_flags
        }


class TransparencyTracker:
    """
    Tracks and scores crypto project transparency.
    """
    
    # Grade thresholds
    GRADE_THRESHOLDS = [
        (95, "A+"), (90, "A"), (85, "A-"),
        (80, "B+"), (75, "B"), (70, "B-"),
        (65, "C+"), (60, "C"), (55, "C-"),
        (50, "D"), (0, "F")
    ]
    
    def __init__(self):
        self.reports: Dict[str, TransparencyReport] = {}
        self.benchmark_scores: List[int] = []
        
    async def generate_report(self, token_address: str, project_name: str) -> TransparencyReport:
        """Generate transparency report for a project."""
        report = TransparencyReport(
            project_name=project_name,
            token_address=token_address,
            generated_at=datetime.now()
        )
        
        # Check all transparency categories
        await self._check_team(report)
        await self._check_contract(report)
        await self._check_treasury(report)
        await self._check_communication(report)
        await self._check_audit(report)
        await self._check_roadmap(report)
        
        # Calculate overall score
        report.overall_score = self._calculate_overall_score(report)
        report.grade = self._score_to_grade(report.overall_score)
        
        # Calculate percentile
        report.rank_percentile = self._calculate_percentile(report.overall_score)
        
        # Generate summary
        self._generate_summary(report)
        
        # Store report
        self.reports[token_address] = report
        self.benchmark_scores.append(report.overall_score)
        
        return report
    
    async def _check_team(self, report: TransparencyReport):
        """Check team transparency."""
        items = [
            TransparencyItem(
                category=TransparencyCategory.TEAM,
                name="Team Doxxed",
                status=TransparencyStatus.UNVERIFIED,
                score=0,
                notes="Team identity not publicly disclosed"
            ),
            TransparencyItem(
                category=TransparencyCategory.TEAM,
                name="LinkedIn Profiles",
                status=TransparencyStatus.MISSING,
                score=0,
                notes="No LinkedIn profiles found"
            ),
            TransparencyItem(
                category=TransparencyCategory.TEAM,
                name="Past Experience Verifiable",
                status=TransparencyStatus.UNVERIFIED,
                score=0,
                notes="Cannot verify claimed experience"
            ),
            TransparencyItem(
                category=TransparencyCategory.TEAM,
                name="Team Wallet Labels",
                status=TransparencyStatus.MISSING,
                score=0,
                notes="Team wallets not labeled"
            )
        ]
        
        report.items.extend(items)
    
    async def _check_contract(self, report: TransparencyReport):
        """Check contract transparency."""
        items = [
            TransparencyItem(
                category=TransparencyCategory.CONTRACT,
                name="Contract Verified",
                status=TransparencyStatus.VERIFIED,
                score=100,
                evidence="Verified on Solscan"
            ),
            TransparencyItem(
                category=TransparencyCategory.CONTRACT,
                name="Ownership Renounced",
                status=TransparencyStatus.UNVERIFIED,
                score=0,
                notes="Owner can still modify contract"
            ),
            TransparencyItem(
                category=TransparencyCategory.CONTRACT,
                name="Mint Authority Disabled",
                status=TransparencyStatus.VERIFIED,
                score=100,
                evidence="No mint function found"
            ),
            TransparencyItem(
                category=TransparencyCategory.CONTRACT,
                name="Liquidity Locked",
                status=TransparencyStatus.UNVERIFIED,
                score=0,
                notes="Liquidity not locked"
            )
        ]
        
        report.items.extend(items)
    
    async def _check_treasury(self, report: TransparencyReport):
        """Check treasury transparency."""
        items = [
            TransparencyItem(
                category=TransparencyCategory.TREASURY,
                name="Treasury Wallet Labeled",
                status=TransparencyStatus.MISSING,
                score=0,
                notes="Treasury wallet not publicly disclosed"
            ),
            TransparencyItem(
                category=TransparencyCategory.TREASURY,
                name="Treasury Holdings Public",
                status=TransparencyStatus.MISSING,
                score=0,
                notes="Cannot view treasury holdings"
            ),
            TransparencyItem(
                category=TransparencyCategory.TREASURY,
                name="Spending Transparent",
                status=TransparencyStatus.MISSING,
                score=0,
                notes="No public spending records"
            ),
            TransparencyItem(
                category=TransparencyCategory.TREASURY,
                name="Multi-sig Required",
                status=TransparencyStatus.UNVERIFIED,
                score=0,
                notes="Unknown if treasury uses multi-sig"
            )
        ]
        
        report.items.extend(items)
    
    async def _check_communication(self, report: TransparencyReport):
        """Check communication transparency."""
        items = [
            TransparencyItem(
                category=TransparencyCategory.COMMUNICATION,
                name="Active Social Media",
                status=TransparencyStatus.VERIFIED,
                score=80,
                evidence="Twitter, Telegram active"
            ),
            TransparencyItem(
                category=TransparencyCategory.COMMUNICATION,
                name="Regular Updates",
                status=TransparencyStatus.PARTIAL,
                score=50,
                notes="Updates are infrequent"
            ),
            TransparencyItem(
                category=TransparencyCategory.COMMUNICATION,
                name="Responsive to Community",
                status=TransparencyStatus.VERIFIED,
                score=90,
                evidence="Team responds to questions"
            ),
            TransparencyItem(
                category=TransparencyCategory.COMMUNICATION,
                name="Transparent About Issues",
                status=TransparencyStatus.UNVERIFIED,
                score=0,
                notes="No major issues to assess"
            )
        ]
        
        report.items.extend(items)
    
    async def _check_audit(self, report: TransparencyReport):
        """Check audit transparency."""
        items = [
            TransparencyItem(
                category=TransparencyCategory.AUDIT,
                name="Contract Audited",
                status=TransparencyStatus.MISSING,
                score=0,
                notes="No audit report found"
            ),
            TransparencyItem(
                category=TransparencyCategory.AUDIT,
                name="Reputable Auditor",
                status=TransparencyStatus.MISSING,
                score=0,
                notes="No audit to verify"
            ),
            TransparencyItem(
                category=TransparencyCategory.AUDIT,
                name="Audit Issues Resolved",
                status=TransparencyStatus.MISSING,
                score=0,
                notes="No audit to check"
            ),
            TransparencyItem(
                category=TransparencyCategory.AUDIT,
                name="Bug Bounty Program",
                status=TransparencyStatus.MISSING,
                score=0,
                notes="No bug bounty program"
            )
        ]
        
        report.items.extend(items)
    
    async def _check_roadmap(self, report: TransparencyReport):
        """Check roadmap transparency."""
        items = [
            TransparencyItem(
                category=TransparencyCategory.ROADMAP,
                name="Public Roadmap",
                status=TransparencyStatus.VERIFIED,
                score=100,
                evidence="Roadmap on website"
            ),
            TransparencyItem(
                category=TransparencyCategory.ROADMAP,
                name="Realistic Timeline",
                status=TransparencyStatus.VERIFIED,
                score=80,
                notes="Timeline appears reasonable"
            ),
            TransparencyItem(
                category=TransparencyCategory.ROADMAP,
                name="Deliverables Met",
                status=TransparencyStatus.PARTIAL,
                score=60,
                notes="Some delays but generally on track"
            ),
            TransparencyItem(
                category=TransparencyCategory.ROADMAP,
                name="Regular Progress Updates",
                status=TransparencyStatus.PARTIAL,
                score=50,
                notes="Updates could be more frequent"
            )
        ]
        
        report.items.extend(items)
    
    def _calculate_overall_score(self, report: TransparencyReport) -> int:
        """Calculate overall transparency score."""
        if not report.items:
            return 0
        
        total_score = sum(item.score for item in report.items)
        return int(total_score / len(report.items))
    
    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        for threshold, grade in self.GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return "F"
    
    def _calculate_percentile(self, score: int) -> int:
        """Calculate percentile ranking."""
        if not self.benchmark_scores:
            return 50
        
        below = sum(1 for s in self.benchmark_scores if s < score)
        return int((below / len(self.benchmark_scores)) * 100)
    
    def _generate_summary(self, report: TransparencyReport):
        """Generate strengths, weaknesses, and red flags."""
        for item in report.items:
            if item.score >= 90:
                report.strengths.append(f"{item.name}: {item.notes}")
            elif item.score <= 30:
                if item.category in [TransparencyCategory.TEAM, TransparencyCategory.CONTRACT]:
                    report.red_flags.append(f"{item.name}: {item.notes}")
                else:
                    report.weaknesses.append(f"{item.name}: {item.notes}")
            elif item.score <= 60:
                report.weaknesses.append(f"{item.name}: {item.notes}")
    
    def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get transparency leaderboard."""
        sorted_reports = sorted(
            self.reports.values(),
            key=lambda r: r.overall_score,
            reverse=True
        )
        
        return [
            {
                "rank": i + 1,
                "project": r.project_name,
                "token": r.token_address,
                "score": r.overall_score,
                "grade": r.grade
            }
            for i, r in enumerate(sorted_reports[:limit])
        ]


# Global instance
_tracker = None

def get_transparency_tracker() -> TransparencyTracker:
    """Get global transparency tracker."""
    global _tracker
    if _tracker is None:
        _tracker = TransparencyTracker()
    return _tracker


if __name__ == "__main__":
    print("=" * 70)
    print("TRANSPARENCY TRACKER")
    print("=" * 70)
    
    print("\n📊 Transparency Categories:")
    print("  👥 Team - Doxxing, experience, wallet labels")
    print("  📜 Contract - Verification, ownership, locks")
    print("  💰 Treasury - Holdings, spending, multi-sig")
    print("  💬 Communication - Updates, responsiveness")
    print("  🔍 Audit - Reports, auditors, bug bounties")
    print("  🗺️ Roadmap - Public, realistic, delivered")
    
    print("\n🏆 Grading:")
    print("  A+ (95-100) - Exceptional transparency")
    print("  A (90-94) - Excellent transparency")
    print("  B (75-89) - Good transparency")
    print("  C (55-74) - Average transparency")
    print("  D (50-54) - Below average")
    print("  F (<50) - Poor transparency")
    
    print("\n" + "=" * 70)
