"""
RMI Content Management System (CMS)
===================================
Complete editorial workflow for the Scam Library and educational content.
Bot writes → Editor reviews → Publish to web/X/Telegram
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
from slugify import slugify


class ContentStatus(Enum):
    """Content workflow states."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    IN_REVIEW = "in_review"
    REVISIONS_NEEDED = "revisions_needed"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class ContentType(Enum):
    """Types of content."""
    SCAM_GUIDE = "scam_guide"
    SAFETY_TIP = "safety_tip"
    RED_FLAG_GUIDE = "red_flag_guide"
    TUTORIAL = "tutorial"
    NEWS_ANALYSIS = "news_analysis"
    CASE_STUDY = "case_study"
    GLOSSARY_TERM = "glossary_term"
    VIDEO_SCRIPT = "video_script"
    THREAD = "thread"
    MEME = "meme"


class ContentPriority(Enum):
    """Content priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class ContentArticle:
    """Content article entity."""
    id: str
    title: str
    slug: str
    content_type: ContentType
    status: ContentStatus
    
    # Content fields
    content: str = ""
    excerpt: str = ""
    key_points: List[str] = field(default_factory=list)
    
    # Metadata
    author_id: str = "bot"  # "bot" or user_id
    editor_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    estimated_read_time: int = 0
    
    # Media
    featured_image: Optional[str] = None
    images: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    
    # SEO
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    
    # Publishing
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    
    # Stats
    view_count: int = 0
    share_count: int = 0
    helpful_count: int = 0
    
    # Related content
    related_scams: List[str] = field(default_factory=list)
    related_tokens: List[str] = field(default_factory=list)
    related_wallets: List[str] = field(default_factory=list)


@dataclass
class EditorialComment:
    """Comment on content during review."""
    id: str
    article_id: str
    author_id: str
    comment: str
    line_number: Optional[int] = None
    is_resolved: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentInbox:
    """Editor's content inbox."""
    pending_review: List[ContentArticle] = field(default_factory=list)
    revisions_needed: List[ContentArticle] = field(default_factory=list)
    scheduled: List[ContentArticle] = field(default_factory=list)
    recently_published: List[ContentArticle] = field(default_factory=list)
    
    @property
    def total_pending(self) -> int:
        return len(self.pending_review) + len(self.revisions_needed)


class ContentCalendar:
    """Content publishing calendar."""
    
    def __init__(self):
        self.scheduled_content: Dict[str, List[ContentArticle]] = {}
    
    def schedule(self, article: ContentArticle, publish_time: datetime):
        """Schedule content for publication."""
        date_key = publish_time.strftime("%Y-%m-%d")
        
        if date_key not in self.scheduled_content:
            self.scheduled_content[date_key] = []
        
        article.scheduled_for = publish_time
        article.status = ContentStatus.SCHEDULED
        self.scheduled_content[date_key].append(article)
    
    def get_upcoming(self, days: int = 7) -> List[ContentArticle]:
        """Get upcoming scheduled content."""
        upcoming = []
        now = datetime.utcnow()
        
        for i in range(days):
            date_key = (now + timedelta(days=i)).strftime("%Y-%m-%d")
            if date_key in self.scheduled_content:
                upcoming.extend(self.scheduled_content[date_key])
        
        return sorted(upcoming, key=lambda x: x.scheduled_for or datetime.max)
    
    def get_daily_slots(self, date: datetime) -> Dict[str, Any]:
        """Get recommended posting slots for a day."""
        return {
            "morning": {"time": "09:00", "type": "educational", "engagement": "high"},
            "lunch": {"time": "12:30", "type": "quick_tip", "engagement": "medium"},
            "afternoon": {"time": "15:00", "type": "case_study", "engagement": "high"},
            "evening": {"time": "19:00", "type": "thread", "engagement": "very_high"},
            "night": {"time": "21:30", "type": "news_analysis", "engagement": "high"}
        }


class ContentBot:
    """
    Bot that writes educational content during off-hours.
    Uses LLM rotation for variety and cost optimization.
    """
    
    CONTENT_TEMPLATES = {
        ContentType.SCAM_GUIDE: {
            "structure": [
                "Introduction - What is this scam?",
                "How it works - Step by step breakdown",
                "Red flags to watch for",
                "Real-world examples",
                "How to protect yourself",
                "What to do if you fell for it",
                "Conclusion"
            ],
            "tone": "educational but accessible",
            "length": "800-1200 words"
        },
        ContentType.SAFETY_TIP: {
            "structure": [
                "The tip in one sentence",
                "Why it matters",
                "How to implement it",
                "Common mistakes",
                "Quick action items"
            ],
            "tone": "concise and actionable",
            "length": "300-500 words"
        },
        ContentType.RED_FLAG_GUIDE: {
            "structure": [
                "Introduction to the red flag",
                "Why it's suspicious",
                "How to spot it",
                "Examples with screenshots",
                "What to do when you see it"
            ],
            "tone": "warning but educational",
            "length": "600-900 words"
        },
        ContentType.CASE_STUDY: {
            "structure": [
                "The project/token",
                "Timeline of events",
                "Warning signs that were missed",
                "The rug pull",
                "Aftermath and lessons",
                "How to spot similar scams"
            ],
            "tone": "investigative storytelling",
            "length": "1000-1500 words"
        },
        ContentType.GLOSSARY_TERM: {
            "structure": [
                "Term definition",
                "Simple explanation",
                "Technical details (optional)",
                "Related terms",
                "Usage examples"
            ],
            "tone": "encyclopedic but readable",
            "length": "200-400 words"
        }
    }
    
    TOPIC_IDEAS = [
        # Scam Types
        {"type": ContentType.SCAM_GUIDE, "topic": "Rug Pull", "priority": ContentPriority.HIGH},
        {"type": ContentType.SCAM_GUIDE, "topic": "Honeypot", "priority": ContentPriority.HIGH},
        {"type": ContentType.SCAM_GUIDE, "topic": "Pump and Dump", "priority": ContentPriority.HIGH},
        {"type": ContentType.SCAM_GUIDE, "topic": "Fake Airdrops", "priority": ContentPriority.HIGH},
        {"type": ContentType.SCAM_GUIDE, "topic": "Phishing Wallets", "priority": ContentPriority.URGENT},
        {"type": ContentType.SCAM_GUIDE, "topic": "Social Engineering", "priority": ContentPriority.HIGH},
        {"type": ContentType.SCAM_GUIDE, "topic": "Impersonation Scams", "priority": ContentPriority.HIGH},
        {"type": ContentType.SCAM_GUIDE, "topic": "Fake Exchanges", "priority": ContentPriority.HIGH},
        {"type": ContentType.SCAM_GUIDE, "topic": "Investment Scams", "priority": ContentPriority.HIGH},
        {"type": ContentType.SCAM_GUIDE, "topic": "Romance Scams", "priority": ContentPriority.MEDIUM},
        
        # Safety Tips
        {"type": ContentType.SAFETY_TIP, "topic": "How to Verify a Contract", "priority": ContentPriority.HIGH},
        {"type": ContentType.SAFETY_TIP, "topic": "Secure Wallet Setup", "priority": ContentPriority.URGENT},
        {"type": ContentType.SAFETY_TIP, "topic": "Seed Phrase Safety", "priority": ContentPriority.URGENT},
        {"type": ContentType.SAFETY_TIP, "topic": "Hardware Wallets", "priority": ContentPriority.HIGH},
        {"type": ContentType.SAFETY_TIP, "topic": "Two-Factor Authentication", "priority": ContentPriority.HIGH},
        {"type": ContentType.SAFETY_TIP, "topic": "Transaction Simulation", "priority": ContentPriority.HIGH},
        {"type": ContentType.SAFETY_TIP, "topic": "Discord Safety", "priority": ContentPriority.MEDIUM},
        {"type": ContentType.SAFETY_TIP, "topic": "Twitter Safety", "priority": ContentPriority.MEDIUM},
        
        # Red Flags
        {"type": ContentType.RED_FLAG_GUIDE, "topic": "Unrealistic Returns", "priority": ContentPriority.HIGH},
        {"type": ContentType.RED_FLAG_GUIDE, "topic": "Anonymous Teams", "priority": ContentPriority.HIGH},
        {"type": ContentType.RED_FLAG_GUIDE, "topic": "No Audit", "priority": ContentPriority.MEDIUM},
        {"type": ContentType.RED_FLAG_GUIDE, "topic": "Copy-Paste Contracts", "priority": ContentPriority.HIGH},
        {"type": ContentType.RED_FLAG_GUIDE, "topic": "Fake Volume", "priority": ContentPriority.HIGH},
        {"type": ContentType.RED_FLAG_GUIDE, "topic": "Whale Concentration", "priority": ContentPriority.MEDIUM},
        {"type": ContentType.RED_FLAG_GUIDE, "topic": "Mint Authority", "priority": ContentPriority.HIGH},
        
        # Glossary
        {"type": ContentType.GLOSSARY_TERM, "topic": "Liquidity", "priority": ContentPriority.LOW},
        {"type": ContentType.GLOSSARY_TERM, "topic": "Market Cap", "priority": ContentPriority.LOW},
        {"type": ContentType.GLOSSARY_TERM, "topic": "FDV", "priority": ContentPriority.LOW},
        {"type": ContentType.GLOSSARY_TERM, "topic": "Slippage", "priority": ContentPriority.LOW},
        {"type": ContentType.GLOSSARY_TERM, "topic": "Gas Fees", "priority": ContentPriority.LOW},
        {"type": ContentType.GLOSSARY_TERM, "topic": "Smart Contract", "priority": ContentPriority.MEDIUM},
        {"type": ContentType.GLOSSARY_TERM, "topic": "DEX vs CEX", "priority": ContentPriority.MEDIUM},
    ]
    
    def __init__(self, llm_rotator=None):
        """Initialize content bot."""
        self.llm_rotator = llm_rotator
        self.articles: List[ContentArticle] = []
        self.generated_count = 0
    
    async def generate_daily_content(self, count: int = 3) -> List[ContentArticle]:
        """Generate content for the day."""
        articles = []
        
        # Sort by priority and pick top topics
        sorted_topics = sorted(
            self.TOPIC_IDEAS,
            key=lambda x: x["priority"].value,
            reverse=True
        )
        
        for topic_data in sorted_topics[:count]:
            article = await self._generate_article(topic_data)
            if article:
                articles.append(article)
                self.articles.append(article)
        
        self.generated_count += len(articles)
        return articles
    
    async def _generate_article(self, topic_data: Dict) -> Optional[ContentArticle]:
        """Generate a single article."""
        content_type = topic_data["type"]
        topic = topic_data["topic"]
        
        template = self.CONTENT_TEMPLATES.get(content_type, {})
        structure = template.get("structure", [])
        
        # Generate content using LLM
        prompt = f"""
Write a {template.get('tone', 'educational')} article about "{topic}" for crypto beginners.

Structure:
{chr(10).join(f"{i+1}. {section}" for i, section in enumerate(structure))}

Target length: {template.get('length', '500-800 words')}

Requirements:
- Use simple language, explain technical terms
- Include specific examples where possible
- Make it actionable - readers should know what to DO
- Include a TL;DR at the top
- Use formatting (headers, bullet points) for readability
- Tone should be helpful, not fear-mongering
"""
        
        try:
            if self.llm_rotator:
                content = await self.llm_rotator.generate(prompt, task_type="content")
            else:
                content = f"[PLACEHOLDER] Article about {topic}"
            
            # Extract excerpt (first 150 chars)
            excerpt = content[:150].strip() + "..." if len(content) > 150 else content
            
            # Generate key points
            key_points = await self._extract_key_points(content)
            
            # Create article
            article_id = hashlib.sha256(f"{topic}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]
            
            article = ContentArticle(
                id=article_id,
                title=f"{topic}: A Complete Guide" if content_type == ContentType.SCAM_GUIDE else topic,
                slug=slugify(topic),
                content_type=content_type,
                status=ContentStatus.PENDING_REVIEW,
                content=content,
                excerpt=excerpt,
                key_points=key_points,
                author_id="bot",
                tags=[topic.lower().replace(" ", "-"), content_type.value],
                categories=[self._get_category(content_type)],
                difficulty_level=self._get_difficulty(content_type),
                estimated_read_time=self._estimate_read_time(content),
                meta_title=f"{topic} | RMI Scam Library",
                meta_description=excerpt,
                keywords=[topic.lower(), "crypto", "scam", "safety"],
                submitted_at=datetime.utcnow()
            )
            
            return article
            
        except Exception as e:
            print(f"Error generating article: {e}")
            return None
    
    async def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content."""
        # In production, use LLM to extract
        lines = content.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if len(line) > 20 and len(key_points) < 5:
                    key_points.append(line[1:].strip())
        
        return key_points[:5]
    
    def _get_category(self, content_type: ContentType) -> str:
        """Get category for content type."""
        category_map = {
            ContentType.SCAM_GUIDE: "scam-types",
            ContentType.SAFETY_TIP: "safety",
            ContentType.RED_FLAG_GUIDE: "red-flags",
            ContentType.TUTORIAL: "tutorials",
            ContentType.CASE_STUDY: "case-studies",
            ContentType.GLOSSARY_TERM: "glossary",
            ContentType.NEWS_ANALYSIS: "news",
            ContentType.VIDEO_SCRIPT: "videos",
            ContentType.THREAD: "social",
            ContentType.MEME: "memes"
        }
        return category_map.get(content_type, "general")
    
    def _get_difficulty(self, content_type: ContentType) -> str:
        """Get difficulty level for content type."""
        difficulty_map = {
            ContentType.SCAM_GUIDE: "beginner",
            ContentType.SAFETY_TIP: "beginner",
            ContentType.RED_FLAG_GUIDE: "beginner",
            ContentType.TUTORIAL: "intermediate",
            ContentType.CASE_STUDY: "intermediate",
            ContentType.GLOSSARY_TERM: "beginner",
            ContentType.NEWS_ANALYSIS: "advanced"
        }
        return difficulty_map.get(content_type, "beginner")
    
    def _estimate_read_time(self, content: str) -> int:
        """Estimate read time in minutes."""
        word_count = len(content.split())
        return max(1, word_count // 200)


class EditorialWorkflow:
    """
    Editorial workflow system.
    Manages content from submission to publication.
    """
    
    def __init__(self):
        self.inbox = ContentInbox()
        self.calendar = ContentCalendar()
        self.comments: Dict[str, List[EditorialComment]] = {}
        self.published: List[ContentArticle] = []
    
    async def submit_for_review(self, article: ContentArticle) -> Dict:
        """Submit article for editorial review."""
        article.status = ContentStatus.PENDING_REVIEW
        article.submitted_at = datetime.utcnow()
        
        self.inbox.pending_review.append(article)
        
        return {
            "status": "submitted",
            "article_id": article.id,
            "title": article.title,
            "message": "Article submitted for review. Check your content inbox.",
            "estimated_review_time": "24-48 hours"
        }
    
    async def start_review(self, article_id: str, editor_id: str) -> Dict:
        """Editor starts reviewing an article."""
        article = self._find_article(article_id)
        if not article:
            return {"error": "Article not found"}
        
        article.status = ContentStatus.IN_REVIEW
        article.editor_id = editor_id
        
        # Move from pending to in-review
        self.inbox.pending_review = [a for a in self.inbox.pending_review if a.id != article_id]
        
        return {
            "status": "in_review",
            "article_id": article_id,
            "editor_id": editor_id,
            "message": "Review started. Add comments and approve or request revisions."
        }
    
    async def add_comment(
        self,
        article_id: str,
        editor_id: str,
        comment: str,
        line_number: Optional[int] = None
    ) -> Dict:
        """Add editorial comment."""
        comment_id = hashlib.sha256(
            f"{article_id}:{editor_id}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]
        
        editorial_comment = EditorialComment(
            id=comment_id,
            article_id=article_id,
            author_id=editor_id,
            comment=comment,
            line_number=line_number
        )
        
        if article_id not in self.comments:
            self.comments[article_id] = []
        
        self.comments[article_id].append(editorial_comment)
        
        return {
            "status": "comment_added",
            "comment_id": comment_id,
            "article_id": article_id
        }
    
    async def approve(self, article_id: str, editor_id: str, notes: str = "") -> Dict:
        """Approve article for publication."""
        article = self._find_article(article_id)
        if not article:
            return {"error": "Article not found"}
        
        article.status = ContentStatus.APPROVED
        article.editor_id = editor_id
        article.reviewed_at = datetime.utcnow()
        
        return {
            "status": "approved",
            "article_id": article_id,
            "title": article.title,
            "editor_notes": notes,
            "next_steps": ["Schedule for publication", "Publish immediately", "Request changes"]
        }
    
    async def request_revisions(
        self,
        article_id: str,
        editor_id: str,
        feedback: str,
        priority_changes: List[str]
    ) -> Dict:
        """Request revisions from bot/author."""
        article = self._find_article(article_id)
        if not article:
            return {"error": "Article not found"}
        
        article.status = ContentStatus.REVISIONS_NEEDED
        article.editor_id = editor_id
        
        # Add feedback as comment
        await self.add_comment(article_id, editor_id, feedback)
        
        self.inbox.revisions_needed.append(article)
        
        return {
            "status": "revisions_needed",
            "article_id": article_id,
            "feedback": feedback,
            "priority_changes": priority_changes,
            "message": "Article returned for revisions. Bot will be notified."
        }
    
    async def schedule_publication(
        self,
        article_id: str,
        publish_time: datetime,
        channels: List[str]
    ) -> Dict:
        """Schedule article for publication."""
        article = self._find_article(article_id)
        if not article:
            return {"error": "Article not found"}
        
        self.calendar.schedule(article, publish_time)
        
        return {
            "status": "scheduled",
            "article_id": article_id,
            "title": article.title,
            "scheduled_for": publish_time.isoformat(),
            "channels": channels,
            "message": f"Article scheduled for {publish_time.strftime('%Y-%m-%d %H:%M')} UTC"
        }
    
    async def publish(
        self,
        article_id: str,
        channels: List[str] = None
    ) -> Dict:
        """Publish article to specified channels."""
        article = self._find_article(article_id)
        if not article:
            return {"error": "Article not found"}
        
        article.status = ContentStatus.PUBLISHED
        article.published_at = datetime.utcnow()
        
        self.published.append(article)
        
        # Remove from scheduled
        for date_key, articles in self.calendar.scheduled_content.items():
            self.calendar.scheduled_content[date_key] = [
                a for a in articles if a.id != article_id
            ]
        
        channels = channels or ["website"]
        
        return {
            "status": "published",
            "article_id": article_id,
            "title": article.title,
            "published_at": article.published_at.isoformat(),
            "channels": channels,
            "urls": {
                "web": f"https://intel.cryptorugmunch.com/library/{article.slug}",
                "api": f"/api/content/article/{article.id}"
            }
        }
    
    async def reject(self, article_id: str, editor_id: str, reason: str) -> Dict:
        """Reject article."""
        article = self._find_article(article_id)
        if not article:
            return {"error": "Article not found"}
        
        article.status = ContentStatus.REJECTED
        article.editor_id = editor_id
        
        await self.add_comment(article_id, editor_id, f"REJECTED: {reason}")
        
        return {
            "status": "rejected",
            "article_id": article_id,
            "reason": reason
        }
    
    def get_inbox(self, editor_id: str) -> Dict:
        """Get editor's content inbox."""
        return {
            "pending_review": [
                {
                    "id": a.id,
                    "title": a.title,
                    "type": a.content_type.value,
                    "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
                    "priority": "high" if a.content_type == ContentType.SCAM_GUIDE else "normal",
                    "excerpt": a.excerpt[:100] + "..."
                }
                for a in self.inbox.pending_review
            ],
            "revisions_needed": [
                {
                    "id": a.id,
                    "title": a.title,
                    "type": a.content_type.value,
                    "comments_count": len(self.comments.get(a.id, []))
                }
                for a in self.inbox.revisions_needed
            ],
            "scheduled": [
                {
                    "id": a.id,
                    "title": a.title,
                    "scheduled_for": a.scheduled_for.isoformat() if a.scheduled_for else None
                }
                for a in self.calendar.get_upcoming(30)
            ],
            "recently_published": [
                {
                    "id": a.id,
                    "title": a.title,
                    "published_at": a.published_at.isoformat() if a.published_at else None,
                    "views": a.view_count
                }
                for a in sorted(self.published, key=lambda x: x.published_at or datetime.min, reverse=True)[:10]
            ],
            "stats": {
                "total_pending": self.inbox.total_pending,
                "published_today": len([a for a in self.published if a.published_at and a.published_at.date() == datetime.utcnow().date()]),
                "scheduled_this_week": len(self.calendar.get_upcoming(7))
            }
        }
    
    def _find_article(self, article_id: str) -> Optional[ContentArticle]:
        """Find article by ID."""
        # Search in all locations
        for article in self.inbox.pending_review:
            if article.id == article_id:
                return article
        
        for article in self.inbox.revisions_needed:
            if article.id == article_id:
                return article
        
        for articles in self.calendar.scheduled_content.values():
            for article in articles:
                if article.id == article_id:
                    return article
        
        for article in self.published:
            if article.id == article_id:
                return article
        
        return None


class ScamLibrary:
    """
    Public-facing Scam Library.
    Searchable database of educational content.
    """
    
    def __init__(self):
        self.articles: List[ContentArticle] = []
        self.categories = {
            "scam-types": "Different types of crypto scams",
            "safety": "How to stay safe in crypto",
            "red-flags": "Warning signs to watch for",
            "tutorials": "Step-by-step guides",
            "case-studies": "Real-world scam breakdowns",
            "glossary": "Crypto terms explained"
        }
        self.learning_paths = {
            "beginner": {
                "name": "Crypto Safety 101",
                "description": "Essential knowledge for new crypto users",
                "articles": [
                    "secure-wallet-setup",
                    "seed-phrase-safety",
                    "common-scams-overview",
                    "red-flags-guide"
                ]
            },
            "intermediate": {
                "name": "Advanced Protection",
                "description": "Deeper dive into crypto security",
                "articles": [
                    "contract-verification",
                    "liquidity-analysis",
                    "wallet-clustering",
                    "kol-evaluation"
                ]
            },
            "advanced": {
                "name": "Expert Investigator",
                "description": "Professional-grade investigation techniques",
                "articles": [
                    "on-chain-analysis",
                    "behavioral-profiling",
                    "cross-chain-tracking",
                    "forensic-reporting"
                ]
            }
        }
    
    async def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search the scam library."""
        results = []
        query_lower = query.lower()
        
        for article in self.articles:
            if article.status != ContentStatus.PUBLISHED:
                continue
            
            score = 0
            
            # Title match
            if query_lower in article.title.lower():
                score += 10
            
            # Content match
            if query_lower in article.content.lower():
                score += 5
            
            # Tags match
            for tag in article.tags:
                if query_lower in tag.lower():
                    score += 3
            
            # Excerpt match
            if query_lower in article.excerpt.lower():
                score += 2
            
            if score > 0:
                results.append({
                    "article": article,
                    "score": score
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return [
            {
                "id": r["article"].id,
                "title": r["article"].title,
                "slug": r["article"].slug,
                "excerpt": r["article"].excerpt,
                "type": r["article"].content_type.value,
                "difficulty": r["article"].difficulty_level,
                "read_time": r["article"].estimated_read_time,
                "published_at": r["article"].published_at.isoformat() if r["article"].published_at else None,
                "score": r["score"]
            }
            for r in results[:20]
        ]
    
    async def get_article(self, slug: str) -> Optional[Dict]:
        """Get article by slug."""
        for article in self.articles:
            if article.slug == slug and article.status == ContentStatus.PUBLISHED:
                # Increment view count
                article.view_count += 1
                
                return {
                    "id": article.id,
                    "title": article.title,
                    "slug": article.slug,
                    "content": article.content,
                    "excerpt": article.excerpt,
                    "key_points": article.key_points,
                    "type": article.content_type.value,
                    "difficulty": article.difficulty_level,
                    "read_time": article.estimated_read_time,
                    "tags": article.tags,
                    "categories": article.categories,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "author": "RMI Research Team" if article.author_id == "bot" else article.author_id,
                    "view_count": article.view_count,
                    "helpful_count": article.helpful_count,
                    "related_articles": await self._get_related(article),
                    "meta": {
                        "title": article.meta_title,
                        "description": article.meta_description,
                        "keywords": article.keywords
                    }
                }
        
        return None
    
    async def get_by_category(self, category: str, page: int = 1, limit: int = 10) -> Dict:
        """Get articles by category."""
        articles = [
            a for a in self.articles
            if category in a.categories and a.status == ContentStatus.PUBLISHED
        ]
        
        total = len(articles)
        start = (page - 1) * limit
        end = start + limit
        
        return {
            "category": category,
            "category_description": self.categories.get(category, ""),
            "articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "slug": a.slug,
                    "excerpt": a.excerpt,
                    "type": a.content_type.value,
                    "difficulty": a.difficulty_level,
                    "read_time": a.estimated_read_time,
                    "published_at": a.published_at.isoformat() if a.published_at else None,
                    "view_count": a.view_count
                }
                for a in articles[start:end]
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    
    async def get_learning_path(self, level: str) -> Optional[Dict]:
        """Get learning path for difficulty level."""
        path = self.learning_paths.get(level)
        if not path:
            return None
        
        articles = []
        for slug in path["articles"]:
            article = await self.get_article(slug)
            if article:
                articles.append(article)
        
        return {
            "level": level,
            "name": path["name"],
            "description": path["description"],
            "articles": articles,
            "progress": 0,  # Would be user-specific
            "estimated_total_time": sum(a.get("read_time", 0) for a in articles)
        }
    
    async def get_popular(self, limit: int = 10) -> List[Dict]:
        """Get most popular articles."""
        published = [a for a in self.articles if a.status == ContentStatus.PUBLISHED]
        published.sort(key=lambda x: x.view_count, reverse=True)
        
        return [
            {
                "id": a.id,
                "title": a.title,
                "slug": a.slug,
                "excerpt": a.excerpt,
                "view_count": a.view_count,
                "type": a.content_type.value
            }
            for a in published[:limit]
        ]
    
    async def get_latest(self, limit: int = 10) -> List[Dict]:
        """Get latest published articles."""
        published = [a for a in self.articles if a.status == ContentStatus.PUBLISHED]
        published.sort(key=lambda x: x.published_at or datetime.min, reverse=True)
        
        return [
            {
                "id": a.id,
                "title": a.title,
                "slug": a.slug,
                "excerpt": a.excerpt,
                "published_at": a.published_at.isoformat() if a.published_at else None,
                "type": a.content_type.value
            }
            for a in published[:limit]
        ]
    
    async def _get_related(self, article: ContentArticle) -> List[Dict]:
        """Get related articles."""
        related = []
        
        for a in self.articles:
            if a.id == article.id or a.status != ContentStatus.PUBLISHED:
                continue
            
            # Same category
            if set(a.categories) & set(article.categories):
                related.append({
                    "id": a.id,
                    "title": a.title,
                    "slug": a.slug,
                    "excerpt": a.excerpt[:100] + "..."
                })
            
            if len(related) >= 3:
                break
        
        return related


# ============== FASTAPI ENDPOINTS ==============

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/content", tags=["Content Management"])

# Global instances
cms_bot = ContentBot()
editorial = EditorialWorkflow()
scam_library = ScamLibrary()


class SubmitArticleRequest(BaseModel):
    article_id: str


class ReviewRequest(BaseModel):
    article_id: str
    editor_id: str


class CommentRequest(BaseModel):
    article_id: str
    editor_id: str
    comment: str
    line_number: Optional[int] = None


class ApproveRequest(BaseModel):
    article_id: str
    editor_id: str
    notes: str = ""


class RevisionRequest(BaseModel):
    article_id: str
    editor_id: str
    feedback: str
    priority_changes: List[str]


class ScheduleRequest(BaseModel):
    article_id: str
    publish_time: datetime
    channels: List[str]


class PublishRequest(BaseModel):
    article_id: str
    channels: Optional[List[str]] = None


@router.post("/bot/generate-daily")
async def generate_daily_content(count: int = 3):
    """Generate daily content from bot."""
    articles = await cms_bot.generate_daily_content(count)
    
    # Auto-submit for review
    for article in articles:
        await editorial.submit_for_review(article)
        scam_library.articles.append(article)
    
    return {
        "generated": len(articles),
        "articles": [
            {
                "id": a.id,
                "title": a.title,
                "type": a.content_type.value,
                "status": a.status.value,
                "submitted": True
            }
            for a in articles
        ]
    }


@router.get("/inbox/{editor_id}")
async def get_editor_inbox(editor_id: str):
    """Get editor's content inbox."""
    return editorial.get_inbox(editor_id)


@router.post("/review/start")
async def start_review(request: ReviewRequest):
    """Start reviewing an article."""
    result = await editorial.start_review(request.article_id, request.editor_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/review/comment")
async def add_comment(request: CommentRequest):
    """Add editorial comment."""
    result = await editorial.add_comment(
        request.article_id,
        request.editor_id,
        request.comment,
        request.line_number
    )
    return result


@router.post("/review/approve")
async def approve_article(request: ApproveRequest):
    """Approve article for publication."""
    result = await editorial.approve(request.article_id, request.editor_id, request.notes)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/review/revisions")
async def request_revisions(request: RevisionRequest):
    """Request revisions on article."""
    result = await editorial.request_revisions(
        request.article_id,
        request.editor_id,
        request.feedback,
        request.priority_changes
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/schedule")
async def schedule_article(request: ScheduleRequest):
    """Schedule article for publication."""
    result = await editorial.schedule_publication(
        request.article_id,
        request.publish_time,
        request.channels
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/publish")
async def publish_article(request: PublishRequest):
    """Publish article."""
    result = await editorial.publish(request.article_id, request.channels)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# Public Scam Library Endpoints

@router.get("/library/search")
async def search_library(q: str, category: Optional[str] = None):
    """Search scam library."""
    filters = {"category": category} if category else {}
    results = await scam_library.search(q, filters)
    return {"query": q, "results": results, "count": len(results)}


@router.get("/library/article/{slug}")
async def get_article(slug: str):
    """Get article by slug."""
    article = await scam_library.get_article(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/library/category/{category}")
async def get_by_category(category: str, page: int = 1, limit: int = 10):
    """Get articles by category."""
    return await scam_library.get_by_category(category, page, limit)


@router.get("/library/learning-path/{level}")
async def get_learning_path(level: str):
    """Get learning path."""
    path = await scam_library.get_learning_path(level)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return path


@router.get("/library/popular")
async def get_popular(limit: int = 10):
    """Get popular articles."""
    return await scam_library.get_popular(limit)


@router.get("/library/latest")
async def get_latest(limit: int = 10):
    """Get latest articles."""
    return await scam_library.get_latest(limit)


@router.get("/library/categories")
async def get_categories():
    """Get all categories."""
    return {
        "categories": [
            {"id": k, "name": v, "article_count": 0}
            for k, v in scam_library.categories.items()
        ]
    }


@router.get("/calendar/upcoming")
async def get_upcoming_content(days: int = 7):
    """Get upcoming scheduled content."""
    upcoming = editorial.calendar.get_upcoming(days)
    return {
        "upcoming": [
            {
                "id": a.id,
                "title": a.title,
                "scheduled_for": a.scheduled_for.isoformat() if a.scheduled_for else None
            }
            for a in upcoming
        ],
        "count": len(upcoming)
    }
