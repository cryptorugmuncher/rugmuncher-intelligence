"""
RMI Social Media Automation
===========================
Automated posting, scheduling, and engagement across X, Telegram, Discord.
Builds following through consistent, valuable content.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import croniter


class Platform(Enum):
    """Social media platforms."""
    X = "x"
    TELEGRAM = "telegram"
    DISCORD = "discord"


class PostType(Enum):
    """Types of social media posts."""
    EDUCATIONAL = "educational"
    ALERT = "alert"
    CASE_STUDY = "case_study"
    TIP = "tip"
    THREAD = "thread"
    MEME = "meme"
    POLL = "poll"
    UPDATE = "update"
    ENGAGEMENT = "engagement"


class ContentTheme(Enum):
    """Content themes for variety."""
    SCAM_AWARENESS = "scam_awareness"
    SECURITY_TIPS = "security_tips"
    RED_FLAGS = "red_flags"
    CASE_BREAKDOWN = "case_breakdown"
    TOOL_SPOTLIGHT = "tool_spotlight"
    KOL_ANALYSIS = "kol_analysis"
    MARKET_INSIGHTS = "market_insights"
    COMMUNITY_SPOTLIGHT = "community_spotlight"
    BEHIND_THE_SCENES = "behind_the_scenes"


@dataclass
class SocialPost:
    """Social media post entity."""
    id: str
    platform: Platform
    post_type: PostType
    content: str
    
    # Media
    images: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    
    # Metadata
    theme: Optional[ContentTheme] = None
    scheduled_for: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    
    # Engagement
    likes: int = 0
    replies: int = 0
    reposts: int = 0
    views: int = 0
    
    # Status
    status: str = "draft"  # draft, scheduled, posted, failed
    error_message: Optional[str] = None
    
    # Thread (for X)
    is_thread: bool = False
    thread_posts: List[str] = field(default_factory=list)
    thread_index: int = 0


@dataclass
class PostTemplate:
    """Template for generating posts."""
    post_type: PostType
    theme: ContentTheme
    templates: List[str]
    hashtags: List[str]
    call_to_action: Optional[str] = None
    optimal_length: tuple = (100, 280)  # min, max chars


class PostTemplateLibrary:
    """Library of post templates for each type and theme."""
    
    TEMPLATES = {
        (PostType.EDUCATIONAL, ContentTheme.SCAM_AWARENESS): PostTemplate(
            post_type=PostType.EDUCATIONAL,
            theme=ContentTheme.SCAM_AWARENESS,
            templates=[
                "🚨 NEW SCAM ALERT: {scam_name}\n\n{description}\n\nHow to protect yourself:\n{protection_tips}\n\nStay safe out there! 🛡️",
                "💡 Did you know? {scam_stat}\n\n{scam_name} scams have stolen over ${amount} this year.\n\nHere's what to watch for:\n{red_flags}",
                "⚠️ Common {scam_name} tactics:\n\n{tactics}\n\nIf you see these signs, RUN! 🏃‍♂️",
            ],
            hashtags=["#CryptoSecurity", "#ScamAlert", "#StaySafe"],
            call_to_action="Follow @RugMunchIntel for daily security tips!"
        ),
        
        (PostType.TIP, ContentTheme.SECURITY_TIPS): PostTemplate(
            post_type=PostType.TIP,
            theme=ContentTheme.SECURITY_TIPS,
            templates=[
                "🔒 Security Tip #{tip_number}:\n\n{tip_title}\n\n{tip_content}\n\nSave this for later! 📌",
                "💎 Pro Tip: {tip_title}\n\n{tip_content}\n\nThis one tip could save you thousands. 💰",
                "🛡️ Daily Reminder:\n\n{tip_content}\n\nRT to save a fren! 🤝",
            ],
            hashtags=["#CryptoTips", "#SecurityFirst", "#DYOR"],
            call_to_action="What security tip has saved you? Drop it below! 👇"
        ),
        
        (PostType.ALERT, ContentTheme.RED_FLAGS): PostTemplate(
            post_type=PostType.ALERT,
            theme=ContentTheme.RED_FLAGS,
            templates=[
                "🚩 RED FLAG ALERT 🚩\n\n{red_flag}\n\nIf you see this, be VERY careful:\n\n{explanation}\n\nStay vigilant! 👀",
                "⚠️ WARNING: {red_flag}\n\n{explanation}\n\nThis is how {scam_type} scams start. Don't fall for it! 🙅‍♂️",
            ],
            hashtags=["#RedFlag", "#CryptoScam", "#Warning"],
            call_to_action="Seen this before? Share your experience! 👇"
        ),
        
        (PostType.CASE_STUDY, ContentTheme.CASE_BREAKDOWN): PostTemplate(
            post_type=PostType.CASE_STUDY,
            theme=ContentTheme.CASE_BREAKDOWN,
            templates=[
                "📊 CASE STUDY: {token_name}\n\nWhat happened:\n{summary}\n\nLessons learned:\n{lessons}\n\nFull breakdown 👇",
                "💀 Another rug pull breakdown:\n\n{token_name} - ${amount} stolen\n\nTimeline:\n{timeline}\n\nHow to spot the next one:",
            ],
            hashtags=["#CaseStudy", "#RugPull", "#CryptoCrime"],
            call_to_action="Read the full investigation on our platform!"
        ),
        
        (PostType.THREAD, ContentTheme.SCAM_AWARENESS): PostTemplate(
            post_type=PostType.THREAD,
            theme=ContentTheme.SCAM_AWARENESS,
            templates=[
                "🧵 THREAD: Everything you need to know about {topic}\n\nMost people lose money because they don't understand this.\n\nLet's fix that. 👇",
                "🧵 ULTIMATE GUIDE: {topic}\n\nI've analyzed 100+ scams to bring you this.\n\nSave this thread. 📌\n\n1/",
            ],
            hashtags=["#Thread", "#CryptoGuide", "#Education"],
            call_to_action="Follow for more crypto security content!"
        ),
        
        (PostType.ENGAGEMENT, ContentTheme.COMMUNITY_SPOTLIGHT): PostTemplate(
            post_type=PostType.ENGAGEMENT,
            theme=ContentTheme.COMMUNITY_SPOTLIGHT,
            templates=[
                "📊 POLL: {question}\n\n{options}\n\nResults in 24h! 📈",
                "🤔 Question of the day:\n\n{question}\n\nDrop your thoughts! 👇",
                "🎉 Community Spotlight:\n\n{highlight}\n\nTag someone who needs to see this! 👇",
            ],
            hashtags=["#Community", "#CryptoFam", "#Together"],
            call_to_action=None
        ),
        
        (PostType.MEME, ContentTheme.BEHIND_THE_SCENES): PostTemplate(
            post_type=PostType.MEME,
            theme=ContentTheme.BEHIND_THE_SCENES,
            templates=[
                "When you see a token with 99% holder concentration... 😅\n\n{meme_caption}",
                "Me checking my wallet after ignoring all the red flags 💀\n\n{meme_caption}",
                "POV: You're about to invest in a project with anonymous devs and no audit 🚩\n\n{meme_caption}",
            ],
            hashtags=["#CryptoMemes", "#Web3Humor", "#Relatable"],
            call_to_action="Tag a fren who needs to see this 😂"
        ),
    }
    
    @classmethod
    def get_template(cls, post_type: PostType, theme: ContentTheme) -> Optional[PostTemplate]:
        """Get template for post type and theme."""
        return cls.TEMPLATES.get((post_type, theme))
    
    @classmethod
    def get_random_template(cls, post_type: Optional[PostType] = None) -> Optional[PostTemplate]:
        """Get random template, optionally filtered by type."""
        templates = list(cls.TEMPLATES.values())
        
        if post_type:
            templates = [t for t in templates if t.post_type == post_type]
        
        return random.choice(templates) if templates else None


class ContentCalendar:
    """
    Content calendar for planned posting.
    """
    
    DAILY_SCHEDULE = {
        "monday": {
            "theme": "Educational",
            "posts": [
                {"time": "09:00", "type": PostType.EDUCATIONAL, "theme": ContentTheme.SCAM_AWARENESS},
                {"time": "15:00", "type": PostType.TIP, "theme": ContentTheme.SECURITY_TIPS},
                {"time": "19:00", "type": PostType.ENGAGEMENT, "theme": ContentTheme.COMMUNITY_SPOTLIGHT},
            ]
        },
        "tuesday": {
            "theme": "Case Studies",
            "posts": [
                {"time": "09:00", "type": PostType.CASE_STUDY, "theme": ContentTheme.CASE_BREAKDOWN},
                {"time": "12:00", "type": PostType.ALERT, "theme": ContentTheme.RED_FLAGS},
                {"time": "18:00", "type": PostType.THREAD, "theme": ContentTheme.SCAM_AWARENESS},
            ]
        },
        "wednesday": {
            "theme": "Tips & Tools",
            "posts": [
                {"time": "09:00", "type": PostType.TIP, "theme": ContentTheme.SECURITY_TIPS},
                {"time": "14:00", "type": PostType.EDUCATIONAL, "theme": ContentTheme.TOOL_SPOTLIGHT},
                {"time": "20:00", "type": PostType.MEME, "theme": ContentTheme.BEHIND_THE_SCENES},
            ]
        },
        "thursday": {
            "theme": "Deep Dives",
            "posts": [
                {"time": "09:00", "type": PostType.THREAD, "theme": ContentTheme.KOL_ANALYSIS},
                {"time": "16:00", "type": PostType.CASE_STUDY, "theme": ContentTheme.CASE_BREAKDOWN},
                {"time": "21:00", "type": PostType.ENGAGEMENT, "theme": ContentTheme.COMMUNITY_SPOTLIGHT},
            ]
        },
        "friday": {
            "theme": "Weekend Prep",
            "posts": [
                {"time": "09:00", "type": PostType.EDUCATIONAL, "theme": ContentTheme.SCAM_AWARENESS},
                {"time": "13:00", "type": PostType.TIP, "theme": ContentTheme.SECURITY_TIPS},
                {"time": "18:00", "type": PostType.MEME, "theme": ContentTheme.BEHIND_THE_SCENES},
            ]
        },
        "saturday": {
            "theme": "Community",
            "posts": [
                {"time": "10:00", "type": PostType.ENGAGEMENT, "theme": ContentTheme.COMMUNITY_SPOTLIGHT},
                {"time": "15:00", "type": PostType.ALERT, "theme": ContentTheme.RED_FLAGS},
                {"time": "20:00", "type": PostType.MEME, "theme": ContentTheme.BEHIND_THE_SCENES},
            ]
        },
        "sunday": {
            "theme": "Weekly Recap",
            "posts": [
                {"time": "10:00", "type": PostType.EDUCATIONAL, "theme": ContentTheme.MARKET_INSIGHTS},
                {"time": "16:00", "type": PostType.THREAD, "theme": ContentTheme.SCAM_AWARENESS},
                {"time": "21:00", "type": PostType.ENGAGEMENT, "theme": ContentTheme.COMMUNITY_SPOTLIGHT},
            ]
        },
    }
    
    def __init__(self):
        self.scheduled_posts: List[SocialPost] = []
        self.posted_posts: List[SocialPost] = []
    
    def generate_weekly_schedule(self) -> List[Dict]:
        """Generate weekly content schedule."""
        schedule = []
        today = datetime.utcnow()
        
        for i, (day_name, day_config) in enumerate(self.DAILY_SCHEDULE.items()):
            day_date = today + timedelta(days=i)
            
            for post_config in day_config["posts"]:
                time_str = post_config["time"]
                hour, minute = map(int, time_str.split(":"))
                
                scheduled_time = day_date.replace(hour=hour, minute=minute, second=0)
                
                schedule.append({
                    "day": day_name,
                    "date": scheduled_time.strftime("%Y-%m-%d"),
                    "time": time_str,
                    "datetime": scheduled_time.isoformat(),
                    "type": post_config["type"].value,
                    "theme": post_config["theme"].value,
                    "theme_description": day_config["theme"]
                })
        
        return schedule
    
    def get_today_schedule(self) -> List[Dict]:
        """Get today's scheduled posts."""
        today_name = datetime.utcnow().strftime("%A").lower()
        day_config = self.DAILY_SCHEDULE.get(today_name, {"posts": []})
        
        schedule = []
        for post_config in day_config["posts"]:
            schedule.append({
                "time": post_config["time"],
                "type": post_config["type"].value,
                "theme": post_config["theme"].value
            })
        
        return schedule
    
    def get_next_post_slot(self) -> Optional[datetime]:
        """Get next available posting slot."""
        now = datetime.utcnow()
        today_name = now.strftime("%A").lower()
        day_config = self.DAILY_SCHEDULE.get(today_name, {"posts": []})
        
        for post_config in day_config["posts"]:
            time_str = post_config["time"]
            hour, minute = map(int, time_str.split(":"))
            
            slot_time = now.replace(hour=hour, minute=minute, second=0)
            
            if slot_time > now:
                return slot_time
        
        # If no slots today, return first slot tomorrow
        tomorrow = now + timedelta(days=1)
        tomorrow_name = tomorrow.strftime("%A").lower()
        tomorrow_config = self.DAILY_SCHEDULE.get(tomorrow_name, {"posts": []})
        
        if tomorrow_config["posts"]:
            first_post = tomorrow_config["posts"][0]
            hour, minute = map(int, first_post["time"].split(":"))
            return tomorrow.replace(hour=hour, minute=minute, second=0)
        
        return None


class SocialMediaBot:
    """
    Automated social media posting bot.
    """
    
    def __init__(self):
        self.calendar = ContentCalendar()
        self.posts: List[SocialPost] = []
        self.stats = {
            "total_posts": 0,
            "posts_by_platform": {},
            "posts_by_type": {},
            "engagement_total": 0
        }
    
    async def generate_post(
        self,
        post_type: PostType,
        theme: ContentTheme,
        variables: Dict[str, str]
    ) -> SocialPost:
        """Generate a social media post."""
        template_data = PostTemplateLibrary.get_template(post_type, theme)
        
        if not template_data:
            template_data = PostTemplateLibrary.get_random_template(post_type)
        
        if not template_data:
            raise ValueError(f"No template found for {post_type.value}/{theme.value}")
        
        # Select random template variant
        template = random.choice(template_data.templates)
        
        # Fill in variables
        try:
            content = template.format(**variables)
        except KeyError as e:
            # Fill missing variables with placeholders
            content = template
            for key in re.findall(r'\{(\w+)\}', template):
                if key not in variables:
                    content = content.replace(f"{{{key}}}", f"[{key}]")
        
        # Add hashtags
        hashtags = " ".join(template_data.hashtags)
        
        # Add CTA if space allows
        if template_data.call_to_action and len(content) + len(hashtags) + len(template_data.call_to_action) < 270:
            content += f"\n\n{template_data.call_to_action}"
        
        content += f"\n\n{hashtags}"
        
        # Create post
        post_id = f"post_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        post = SocialPost(
            id=post_id,
            platform=Platform.X,  # Default to X
            post_type=post_type,
            theme=theme,
            content=content
        )
        
        self.posts.append(post)
        return post
    
    async def schedule_post(
        self,
        post: SocialPost,
        scheduled_time: Optional[datetime] = None
    ) -> Dict:
        """Schedule a post."""
        if not scheduled_time:
            scheduled_time = self.calendar.get_next_post_slot()
        
        post.scheduled_for = scheduled_time
        post.status = "scheduled"
        
        self.calendar.scheduled_posts.append(post)
        
        return {
            "post_id": post.id,
            "scheduled_for": scheduled_time.isoformat(),
            "platform": post.platform.value,
            "type": post.post_type.value,
            "content_preview": post.content[:100] + "..."
        }
    
    async def generate_daily_content(self) -> List[SocialPost]:
        """Generate all posts for today."""
        today_schedule = self.calendar.get_today_schedule()
        posts = []
        
        for slot in today_schedule:
            post_type = PostType(slot["type"])
            theme = ContentTheme(slot["theme"])
            
            # Generate variables based on theme
            variables = self._generate_variables(theme)
            
            try:
                post = await self.generate_post(post_type, theme, variables)
                
                # Parse time and schedule
                hour, minute = map(int, slot["time"].split(":"))
                scheduled_time = datetime.utcnow().replace(hour=hour, minute=minute, second=0)
                
                if scheduled_time < datetime.utcnow():
                    scheduled_time += timedelta(days=1)
                
                await self.schedule_post(post, scheduled_time)
                posts.append(post)
                
            except Exception as e:
                print(f"Error generating post: {e}")
        
        return posts
    
    def _generate_variables(self, theme: ContentTheme) -> Dict[str, str]:
        """Generate template variables based on theme."""
        variables = {
            "scam_name": random.choice(["Rug Pull", "Honeypot", "Pump & Dump", "Fake Airdrop", "Phishing"]),
            "tip_number": str(random.randint(1, 50)),
            "tip_title": random.choice([
                "Always Verify the Contract",
                "Check the Liquidity",
                "Never Share Your Seed Phrase",
                "Use a Hardware Wallet",
                "Enable 2FA Everywhere"
            ]),
            "tip_content": random.choice([
                "Before investing, always verify the token contract on a block explorer.",
                "Check if liquidity is locked and for how long.",
                "Your seed phrase is the key to your wallet. Never share it with anyone.",
                "Hardware wallets keep your private keys offline and secure.",
                "Two-factor authentication adds an extra layer of security."
            ]),
            "red_flag": random.choice([
                "Anonymous team with no LinkedIn",
                "Promises of guaranteed returns",
                "No contract audit",
                "Unrealistic APY",
                "Copy-paste website"
            ]),
            "amount": f"{random.randint(1, 100)}M",
            "topic": random.choice([
                "Rug Pulls",
                "Honeypots",
                "Wallet Security",
                "Red Flags",
                "Due Diligence"
            ]),
            "question": random.choice([
                "What's the biggest red flag for you?",
                "Have you ever been rugged?",
                "What security tool do you use?",
                "How do you research projects?"
            ]),
            "meme_caption": random.choice([
                "*nervous sweating*",
                "We've all been there 😅",
                "Learn from others' mistakes!",
                "Don't be this person 💀"
            ]),
        }
        
        return variables
    
    def get_scheduled_posts(self) -> List[Dict]:
        """Get all scheduled posts."""
        return [
            {
                "id": post.id,
                "platform": post.platform.value,
                "type": post.post_type.value,
                "theme": post.theme.value if post.theme else None,
                "scheduled_for": post.scheduled_for.isoformat() if post.scheduled_for else None,
                "content_preview": post.content[:100] + "...",
                "status": post.status
            }
            for post in self.calendar.scheduled_posts
            if post.status == "scheduled"
        ]
    
    def get_stats(self) -> Dict:
        """Get bot statistics."""
        return {
            "total_posts": len(self.posts),
            "scheduled": len([p for p in self.posts if p.status == "scheduled"]),
            "posted": len([p for p in self.posts if p.status == "posted"]),
            "failed": len([p for p in self.posts if p.status == "failed"]),
            "by_platform": {
                platform.value: len([p for p in self.posts if p.platform == platform])
                for platform in Platform
            },
            "by_type": {
                post_type.value: len([p for p in self.posts if p.post_type == post_type])
                for post_type in PostType
            }
        }


class EngagementTracker:
    """
    Tracks engagement metrics across platforms.
    """
    
    def __init__(self):
        self.metrics: Dict[str, Dict] = {}
    
    async def track_post(self, post_id: str, platform: Platform) -> Dict:
        """Track metrics for a post."""
        # In production, fetch from platform APIs
        metrics = {
            "post_id": post_id,
            "platform": platform.value,
            "likes": random.randint(10, 500),
            "replies": random.randint(0, 50),
            "reposts": random.randint(5, 100),
            "views": random.randint(1000, 50000),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.metrics[post_id] = metrics
        return metrics
    
    def get_top_performing(self, limit: int = 10) -> List[Dict]:
        """Get top performing posts."""
        sorted_posts = sorted(
            self.metrics.values(),
            key=lambda x: x["likes"] + x["reposts"] * 2,
            reverse=True
        )
        
        return sorted_posts[:limit]
    
    def get_daily_summary(self) -> Dict:
        """Get daily engagement summary."""
        today = datetime.utcnow().date()
        today_metrics = [
            m for m in self.metrics.values()
            if datetime.fromisoformat(m["timestamp"]).date() == today
        ]
        
        return {
            "date": today.isoformat(),
            "total_posts": len(today_metrics),
            "total_likes": sum(m["likes"] for m in today_metrics),
            "total_replies": sum(m["replies"] for m in today_metrics),
            "total_reposts": sum(m["reposts"] for m in today_metrics),
            "total_views": sum(m["views"] for m in today_metrics),
            "avg_engagement": sum(m["likes"] + m["replies"] + m["reposts"] for m in today_metrics) / len(today_metrics) if today_metrics else 0
        }


# ============== FASTAPI ENDPOINTS ==============

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/social", tags=["Social Media Automation"])

# Global instances
social_bot = SocialMediaBot()
engagement_tracker = EngagementTracker()


class GeneratePostRequest(BaseModel):
    post_type: str
    theme: str
    variables: Dict[str, str]


class SchedulePostRequest(BaseModel):
    post_id: str
    scheduled_for: Optional[datetime] = None


@router.post("/generate")
async def generate_post(request: GeneratePostRequest):
    """Generate a social media post."""
    try:
        post_type = PostType(request.post_type)
        theme = ContentTheme(request.theme)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid type or theme: {e}")
    
    post = await social_bot.generate_post(post_type, theme, request.variables)
    
    return {
        "post_id": post.id,
        "platform": post.platform.value,
        "type": post.post_type.value,
        "theme": post.theme.value if post.theme else None,
        "content": post.content,
        "length": len(post.content)
    }


@router.post("/schedule")
async def schedule_post(request: SchedulePostRequest):
    """Schedule a post."""
    # Find post
    post = None
    for p in social_bot.posts:
        if p.id == request.post_id:
            post = p
            break
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    result = await social_bot.schedule_post(post, request.scheduled_for)
    return result


@router.post("/generate-daily")
async def generate_daily_content():
    """Generate all posts for today."""
    posts = await social_bot.generate_daily_content()
    
    return {
        "generated": len(posts),
        "posts": [
            {
                "id": p.id,
                "type": p.post_type.value,
                "theme": p.theme.value if p.theme else None,
                "scheduled_for": p.scheduled_for.isoformat() if p.scheduled_for else None,
                "content_preview": p.content[:80] + "..."
            }
            for p in posts
        ]
    }


@router.get("/scheduled")
async def get_scheduled_posts():
    """Get all scheduled posts."""
    return {
        "scheduled": social_bot.get_scheduled_posts(),
        "count": len(social_bot.get_scheduled_posts())
    }


@router.get("/calendar/weekly")
async def get_weekly_calendar():
    """Get weekly content calendar."""
    return {
        "schedule": social_bot.calendar.generate_weekly_schedule()
    }


@router.get("/calendar/today")
async def get_today_calendar():
    """Get today's content schedule."""
    return {
        "today": datetime.utcnow().strftime("%A"),
        "schedule": social_bot.calendar.get_today_schedule()
    }


@router.get("/templates")
async def get_templates():
    """Get available post templates."""
    templates = []
    for (post_type, theme), template in PostTemplateLibrary.TEMPLATES.items():
        templates.append({
            "type": post_type.value,
            "theme": theme.value,
            "hashtags": template.hashtags,
            "template_count": len(template.templates)
        })
    
    return {"templates": templates}


@router.get("/stats")
async def get_social_stats():
    """Get social media statistics."""
    return social_bot.get_stats()


@router.get("/engagement/summary")
async def get_engagement_summary():
    """Get engagement summary."""
    return engagement_tracker.get_daily_summary()


@router.get("/engagement/top")
async def get_top_posts(limit: int = 10):
    """Get top performing posts."""
    return {
        "top_posts": engagement_tracker.get_top_performing(limit)
    }
