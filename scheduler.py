"""
Scheduling and distribution algorithm for content calendar.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
from models import Post, ContentType, CalendarEntry, ContentCalendar, CompanyInfo, Persona


class Scheduler:
    """Handles scheduling and distribution of posts and replies."""
    
    def __init__(
        self,
        posts_per_week: int,
        subreddits: List[str],
        personas: List[Persona]
    ):
        self.posts_per_week = posts_per_week
        self.subreddits = subreddits
        self.personas = personas
        self.max_posts_per_subreddit = max(1, posts_per_week // len(subreddits) + 1)
    
    def distribute_posts(
        self,
        week_start: datetime,
        post_data: List[dict]  # List of {title, content, persona, subreddit, query}
    ) -> List[Post]:
        """
        Distribute posts across the week with smart scheduling.
        
        Args:
            week_start: Start of the week
            post_data: Generated post content
            
        Returns:
            List of scheduled Post objects
        """
        posts = []
        week_days = 7
        hours_per_day = [9, 11, 14, 16, 18]  # Business hours for posting
        
        # Distribute posts across weekdays (avoid weekends for better engagement)
        weekday_slots = []
        for day_offset in range(week_days):
            day = week_start + timedelta(days=day_offset)
            if day.weekday() < 5:  # Monday-Friday
                for hour in hours_per_day:
                    weekday_slots.append((day, hour))
        
        # Shuffle and select slots
        random.shuffle(weekday_slots)
        selected_slots = weekday_slots[:len(post_data)]
        selected_slots.sort()  # Sort chronologically
        
        for i, slot in enumerate(selected_slots):
            day, hour = slot
            post_time = day.replace(hour=hour, minute=random.randint(0, 59))
            
            post = Post(
                id=f"P{i+1}",  # P1, P2, P3 format
                date=post_time,
                persona=post_data[i]["persona"],
                username=post_data[i]["username"],
                subreddit=post_data[i]["subreddit"],
                title=post_data[i]["title"],
                content=post_data[i]["content"],
                content_type=ContentType.POST,
                thread_id=f"thread_{i+1}",
                keyword_ids=post_data[i].get("keyword_ids", [])
            )
            posts.append(post)
        
        return posts
    
    def schedule_replies(
        self,
        posts: List[Post],
        reply_data: Dict[str, dict]  # {post_id: {content, persona, username}}
    ) -> List[Post]:
        """
        Schedule replies to posts with natural timing.
        Supports multiple replies per post and nested replies.
        
        Args:
            posts: Original posts
            reply_data: Generated reply content keyed by post_id
            
        Returns:
            List of Reply Post objects
        """
        replies = []
        comment_counter = 1  # C1, C2, C3, etc.
        
        for post in posts:
            if post.id not in reply_data:
                continue
            
            reply_info = reply_data[post.id]
            
            # Generate 1-3 replies per post (70% chance of 1, 20% chance of 2, 10% chance of 3)
            num_replies = 1
            rand = random.random()
            if rand < 0.1:
                num_replies = 3
            elif rand < 0.3:
                num_replies = 2
            
            # Get all existing replies for this post to support nested replies
            existing_replies = [r for r in replies if r.parent_post_id == post.id]
            
            for reply_num in range(num_replies):
                # Schedule reply 15 minutes to 24 hours after original post (or previous reply)
                if reply_num == 0:
                    base_time = post.date
                    hours_delay = random.randint(1, 24)  # First reply: 1-24 hours
                else:
                    base_time = replies[-1].date if replies else post.date
                    hours_delay = random.randint(1, 6)  # Subsequent replies: 1-6 hours
                
                reply_time = base_time + timedelta(hours=hours_delay, minutes=random.randint(0, 59))
                
                # Ensure reply is within the same week
                week_end = post.date + timedelta(days=7)
                if reply_time > week_end:
                    reply_time = post.date + timedelta(hours=random.randint(1, 12))
                
                # Determine if this is a nested reply (reply to a comment)
                parent_comment_id = None
                if reply_num > 0 and existing_replies:
                    # 30% chance of replying to a previous comment
                    if random.random() < 0.3:
                        parent_comment_id = random.choice(existing_replies).id
                
                # Select persona for this reply (different from post author)
                if reply_num == 0:
                    reply_persona = reply_info["persona"]
                    reply_username = reply_info["username"]
                else:
                    # For subsequent replies, use different personas
                    available_personas = [p for p in self.personas if p.username != post.username]
                    if existing_replies:
                        available_personas = [p for p in available_personas if p.username != existing_replies[-1].username]
                    if available_personas:
                        selected_persona = random.choice(available_personas)
                        reply_persona = selected_persona.name
                        reply_username = selected_persona.username
                    else:
                        reply_persona = reply_info["persona"]
                        reply_username = reply_info["username"]
                
                reply = Post(
                    id=f"C{comment_counter}",  # C1, C2, C3 format
                    date=reply_time,
                    persona=reply_persona,
                    username=reply_username,
                    subreddit=post.subreddit,
                    title="",  # Comments don't have titles
                    content=reply_info["content"] if reply_num == 0 else self._generate_nested_reply(post, existing_replies),
                    content_type=ContentType.REPLY,
                    parent_post_id=post.id,
                    parent_comment_id=parent_comment_id,
                    thread_id=post.thread_id
                )
                replies.append(reply)
                comment_counter += 1
                
                # Update existing_replies for next iteration
                existing_replies.append(reply)
        
        return replies
    
    def _generate_nested_reply(self, post: Post, existing_replies: List[Post]) -> str:
        """Generate a simple nested reply."""
        # Simple fallback responses that sound natural
        responses = [
            "Thanks for sharing! I've had similar experiences.",
            "Great point! I've found this helpful too.",
            "This is exactly what I needed to hear.",
            "Same here! This has been a game changer for me.",
            "Appreciate the insight! Going to try this out.",
            "This resonates with me. Thanks for the tip!"
        ]
        return random.choice(responses)
    
    def assign_subreddits(self, num_posts: int) -> List[str]:
        """
        Assign subreddits to posts, avoiding overposting.
        
        Returns:
            List of subreddit names
        """
        assignments = []
        subreddit_counts = {sub: 0 for sub in self.subreddits}
        
        for _ in range(num_posts):
            # Find subreddits that haven't exceeded limit
            available = [
                sub for sub, count in subreddit_counts.items()
                if count < self.max_posts_per_subreddit
            ]
            
            if not available:
                # If all are at limit, reset and use all
                available = self.subreddits
            
            # Weight towards less-used subreddits
            weights = [1.0 / (subreddit_counts[sub] + 1) for sub in available]
            selected = random.choices(available, weights=weights)[0]
            
            assignments.append(selected)
            subreddit_counts[selected] += 1
        
        return assignments
    
    def assign_personas(self, num_posts: int) -> List[str]:
        """
        Assign personas to posts, rotating for variety.
        
        Returns:
            List of persona usernames
        """
        assignments = []
        persona_usernames = [p.username for p in self.personas]
        
        for i in range(num_posts):
            # Rotate personas
            persona = persona_usernames[i % len(persona_usernames)]
            assignments.append(persona)
        
        # Shuffle to avoid predictable patterns
        random.shuffle(assignments)
        return assignments
    
    def create_calendar(
        self,
        week_start: datetime,
        posts: List[Post],
        replies: List[Post]
    ) -> ContentCalendar:
        """
        Create a ContentCalendar from posts and replies.
        
        Args:
            week_start: Start of the week
            posts: List of posts
            replies: List of replies
            
        Returns:
            ContentCalendar object
        """
        all_content = posts + replies
        all_content.sort(key=lambda x: x.date)
        
        entries = []
        for content in all_content:
            entry = CalendarEntry(
                post_id=content.id if content.content_type == ContentType.POST else None,
                comment_id=content.id if content.content_type == ContentType.REPLY else None,
                date=content.date,
                time=content.date.strftime("%I:%M %p"),
                type=content.content_type,
                persona=content.persona,
                username=content.username,
                subreddit=content.subreddit,
                title=content.title,
                content=content.content,
                parent_post_id=content.parent_post_id,
                parent_comment_id=content.parent_comment_id,
                thread_id=content.thread_id,
                keyword_ids=content.keyword_ids if hasattr(content, 'keyword_ids') else []
            )
            entries.append(entry)
        
        week_end = week_start + timedelta(days=7)
        
        return ContentCalendar(
            week_start=week_start,
            week_end=week_end,
            entries=entries,
            metadata={
                "total_posts": len(posts),
                "total_replies": len(replies),
                "subreddits_used": list(set(e.subreddit for e in entries))
            }
        )

