"""
Quality validation system for content calendars.
"""
from typing import List, Dict, Tuple
from models import ContentCalendar, CalendarEntry, ContentType


class QualityValidator:
    """Validates content calendar quality and catches edge cases."""
    
    def __init__(self):
        self.warnings = []
        self.errors = []
    
    def validate(self, calendar: ContentCalendar) -> Tuple[float, List[str]]:
        """
        Validate calendar quality and return score + warnings.
        
        Returns:
            (quality_score, warnings_list)
            quality_score: 0-10 scale
        """
        self.warnings = []
        self.errors = []
        
        score = 10.0
        
        # Check 1: Subreddit distribution
        score -= self._check_subreddit_distribution(calendar)
        
        # Check 2: Topic overlap
        score -= self._check_topic_overlap(calendar)
        
        # Check 3: Persona consistency
        score -= self._check_persona_patterns(calendar)
        
        # Check 4: Timing issues
        score -= self._check_timing_issues(calendar)
        
        # Check 5: Conversation flow
        score -= self._check_conversation_flow(calendar)
        
        # Check 6: Reply distribution
        score -= self._check_reply_distribution(calendar)
        
        # Ensure score is between 0 and 10
        score = max(0.0, min(10.0, score))
        
        return score, self.warnings
    
    def _check_subreddit_distribution(self, calendar: ContentCalendar) -> float:
        """Check if posts are evenly distributed across subreddits."""
        subreddit_counts = {}
        for entry in calendar.entries:
            if entry.type == ContentType.POST:
                subreddit_counts[entry.subreddit] = subreddit_counts.get(entry.subreddit, 0) + 1
        
        if not subreddit_counts:
            return 0.0
        
        max_count = max(subreddit_counts.values())
        min_count = min(subreddit_counts.values())
        
        # Penalize if one subreddit has 2+ more posts than others
        if max_count - min_count > 2:
            self.warnings.append(
                f"Uneven subreddit distribution: {subreddit_counts}. "
                f"Consider spreading posts more evenly."
            )
            return 1.5
        
        # Penalize if any subreddit has more than 2 posts
        if max_count > 2:
            self.warnings.append(
                f"Subreddit {max(subreddit_counts, key=subreddit_counts.get)} has {max_count} posts. "
                f"Consider limiting to 1-2 posts per subreddit per week."
            )
            return 1.0
        
        return 0.0
    
    def _check_topic_overlap(self, calendar: ContentCalendar) -> float:
        """Check for overlapping topics on the same day."""
        daily_topics = {}
        for entry in calendar.entries:
            if entry.type == ContentType.POST:
                day = entry.date.date()
                if day not in daily_topics:
                    daily_topics[day] = []
                daily_topics[day].append(entry.title.lower())
        
        penalty = 0.0
        for day, topics in daily_topics.items():
            # Check for similar titles (simple word overlap check)
            for i, topic1 in enumerate(topics):
                for topic2 in topics[i+1:]:
                    words1 = set(topic1.split())
                    words2 = set(topic2.split())
                    overlap = len(words1 & words2) / max(len(words1), len(words2))
                    
                    if overlap > 0.4:  # 40% word overlap
                        self.warnings.append(
                            f"Similar topics on {day}: '{topic1}' and '{topic2}'"
                        )
                        penalty += 0.5
        
        return min(penalty, 1.5)
    
    def _check_persona_patterns(self, calendar: ContentCalendar) -> float:
        """Check for awkward persona patterns."""
        persona_sequence = []
        for entry in calendar.entries:
            if entry.type == ContentType.POST:
                persona_sequence.append(entry.persona)
        
        # Check if same persona posts consecutively too often
        consecutive_count = 1
        max_consecutive = 1
        for i in range(1, len(persona_sequence)):
            if persona_sequence[i] == persona_sequence[i-1]:
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 1
        
        if max_consecutive > 2:
            self.warnings.append(
                f"Same persona ({persona_sequence[0]}) posts {max_consecutive} times consecutively. "
                f"Consider rotating personas more."
            )
            return 0.5
        
        return 0.0
    
    def _check_timing_issues(self, calendar: ContentCalendar) -> float:
        """Check for timing problems (posts too close together, etc.)."""
        posts = [e for e in calendar.entries if e.type == ContentType.POST]
        posts.sort(key=lambda x: x.date)
        
        penalty = 0.0
        for i in range(len(posts) - 1):
            time_diff = (posts[i+1].date - posts[i].date).total_seconds() / 3600  # hours
            
            # Penalize if posts are less than 4 hours apart
            if time_diff < 4:
                self.warnings.append(
                    f"Posts scheduled too close together: "
                    f"{posts[i].date.strftime('%Y-%m-%d %H:%M')} and "
                    f"{posts[i+1].date.strftime('%Y-%m-%d %H:%M')} "
                    f"({time_diff:.1f} hours apart)"
                )
                penalty += 0.3
        
        return min(penalty, 1.0)
    
    def _check_conversation_flow(self, calendar: ContentCalendar) -> float:
        """Check if replies make sense in context."""
        threads = {}
        for entry in calendar.entries:
            if entry.thread_id:
                if entry.thread_id not in threads:
                    threads[entry.thread_id] = []
                threads[entry.thread_id].append(entry)
        
        penalty = 0.0
        for thread_id, thread_entries in threads.items():
            # Check if reply comes before post (shouldn't happen)
            posts = [e for e in thread_entries if e.type == ContentType.POST]
            replies = [e for e in thread_entries if e.type == ContentType.REPLY]
            
            if posts and replies:
                first_post = min(posts, key=lambda x: x.date)
                for reply in replies:
                    if reply.date < first_post.date:
                        self.warnings.append(
                            f"Reply scheduled before original post in thread {thread_id}"
                        )
                        penalty += 1.0
                
                # Check if multiple replies from same persona in same thread
                reply_personas = [r.persona for r in replies]
                if len(reply_personas) != len(set(reply_personas)):
                    self.warnings.append(
                        f"Same persona replies multiple times in thread {thread_id}"
                    )
                    penalty += 0.5
        
        return min(penalty, 2.0)
    
    def _check_reply_distribution(self, calendar: ContentCalendar) -> float:
        """Check if replies are well-distributed."""
        posts = [e for e in calendar.entries if e.type == ContentType.POST]
        replies = [e for e in calendar.entries if e.type == ContentType.REPLY]
        
        if not posts:
            return 0.0
        
        reply_ratio = len(replies) / len(posts)
        
        # Ideal: 1-2 replies per post
        if reply_ratio < 0.5:
            self.warnings.append(
                f"Low reply ratio: {len(replies)} replies for {len(posts)} posts. "
                f"Consider adding more engagement."
            )
            return 0.5
        
        if reply_ratio > 3:
            self.warnings.append(
                f"High reply ratio: {len(replies)} replies for {len(posts)} posts. "
                f"May look unnatural."
            )
            return 0.5
        
        return 0.0

