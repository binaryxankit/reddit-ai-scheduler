"""
Main orchestrator for generating content calendars.
"""
from datetime import datetime, timedelta
from typing import List, Dict
import random
from models import (
    CalendarRequest, CalendarResponse, ContentCalendar,
    CompanyInfo, Persona, Post, ContentType
)
from content_generator import ContentGenerator
from scheduler import Scheduler
from validator import QualityValidator


class CalendarGenerator:
    """Main class that orchestrates calendar generation."""
    
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.validator = QualityValidator()
    
    def generate_calendar(self, request: CalendarRequest) -> CalendarResponse:
        """
        Generate a complete content calendar.
        
        Args:
            request: CalendarRequest with all inputs
            
        Returns:
            CalendarResponse with calendar and quality metrics
        """
        # Determine week start
        if request.week_start:
            week_start = request.week_start
        else:
            # Start from next Monday
            today = datetime.now()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            week_start = (today + timedelta(days=days_until_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        
        # Initialize scheduler
        scheduler = Scheduler(
            posts_per_week=request.posts_per_week,
            subreddits=request.subreddits,
            personas=request.personas
        )
        
        # Step 1: Assign subreddits and personas to posts
        subreddit_assignments = scheduler.assign_subreddits(request.posts_per_week)
        persona_usernames = scheduler.assign_personas(request.posts_per_week)  # Returns usernames
        
        # Step 2: Generate post content
        posts_data = []
        existing_posts = []
        
        for i in range(request.posts_per_week):
            # Select keywords (use 1-3 keywords per post)
            num_keywords = random.randint(1, 3)
            selected_keywords = random.sample(request.keywords, min(num_keywords, len(request.keywords)))
            keyword_ids = [kw.keyword_id for kw in selected_keywords]
            keyword_texts = [kw.keyword for kw in selected_keywords]
            query = ", ".join(keyword_texts)  # Combine keywords for context
            
            # Get persona object
            persona = next(p for p in request.personas if p.username == persona_usernames[i])
            
            # Generate post
            try:
                post_content = self.content_generator.generate_post(
                    company=request.company_info,
                    persona=persona,
                    subreddit=subreddit_assignments[i],
                    query=query,
                    keywords=keyword_texts if keyword_texts else None,
                    existing_posts=existing_posts
                )
            except Exception as e:
                # Groq failed - return error with helpful message
                error_msg = str(e)
                raise Exception(
                    f"Failed to generate post {i+1}/{request.posts_per_week} for {persona.name} in r/{subreddit_assignments[i]}. "
                    f"Groq API error: {error_msg}. "
                    f"Please check your GROQ_API_KEY in .env file and verify it's valid at https://console.groq.com/"
                )
            
            posts_data.append({
                "title": post_content["title"],
                "content": post_content["content"],
                "persona": persona.name,
                "username": persona.username,
                "subreddit": subreddit_assignments[i],
                "query": query,
                "keyword_ids": keyword_ids
            })
            
            # Create temporary post for overlap checking
            temp_post = Post(
                id=f"temp_{i}",
                date=datetime.now(),
                persona=persona.name,
                username=persona.username,
                subreddit=subreddit_assignments[i],
                title=post_content["title"],
                content=post_content["content"],
                content_type=ContentType.POST,
                keyword_ids=keyword_ids
            )
            existing_posts.append(temp_post)
        
        # Step 3: Schedule posts
        posts = scheduler.distribute_posts(week_start, posts_data)
        
        # Step 4: Generate replies
        reply_data = {}
        for post in posts:
            # Decide if this post should get a reply (70% chance)
            if random.random() < 0.7:
                # Select a different persona for reply
                reply_persona = random.choice([
                    p for p in request.personas if p.username != post.username
                ])
                
                # Get thread posts for context
                thread_posts = [p for p in posts if p.thread_id == post.thread_id]
                
                # Generate reply
                try:
                    reply_content = self.content_generator.generate_reply(
                        company=request.company_info,
                        persona=reply_persona,
                        parent_post=post,
                        thread_posts=thread_posts,
                        subreddit=post.subreddit
                    )
                    
                    # Only add reply if Groq successfully generated it (not None)
                    if reply_content:
                        reply_data[post.id] = {
                            "content": reply_content,
                            "persona": reply_persona.name,
                            "username": reply_persona.username
                        }
                    else:
                        # Groq failed but we continue without this reply
                        print(f"⚠️  Skipping reply for post {post.id} - Groq returned None")
                except Exception as e:
                    # Groq failed for reply - log but continue (replies are optional)
                    print(f"⚠️  Failed to generate reply for post {post.id}: {e}")
                    # Continue without this reply
        
        # Step 5: Schedule replies
        replies = scheduler.schedule_replies(posts, reply_data)
        
        # Step 6: Create calendar
        calendar = scheduler.create_calendar(week_start, posts, replies)
        
        # Step 7: Validate quality
        quality_score, warnings = self.validator.validate(calendar)
        
        return CalendarResponse(
            calendar=calendar,
            quality_score=quality_score,
            warnings=warnings
        )
    
    def generate_next_week(self, request: CalendarRequest, current_week_start: datetime) -> CalendarResponse:
        """
        Generate calendar for the next week.
        
        Args:
            request: Original CalendarRequest
            current_week_start: Start of current week
            
        Returns:
            CalendarResponse for next week
        """
        # Set week_start to next week
        next_week_start = current_week_start + timedelta(days=7)
        request.week_start = next_week_start
        
        return self.generate_calendar(request)

