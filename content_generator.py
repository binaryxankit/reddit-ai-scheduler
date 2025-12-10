"""
Content generation engine using Groq API (OpenAI-compatible).
"""
import os
import json
import re
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from models import CompanyInfo, Persona, Post, ContentType

# Load .env file with explicit path and encoding
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path, override=True)
else:
    # Try loading from current directory
    load_dotenv(override=True)

class ContentGenerator:
    """Generates natural Reddit posts and replies using Groq API."""
    
    def __init__(self):
        # Try multiple ways to get the API key
        api_key = os.getenv("GROQ_API_KEY")
        
        # If not found, try reading .env file directly from multiple locations
        if not api_key:
            # Try current directory first, then file's directory
            current_dir = os.getcwd()
            file_dir = os.path.dirname(os.path.abspath(__file__))
            env_paths = [
                os.path.join(current_dir, '.env'),
                os.path.join(file_dir, '.env'),
                '.env'
            ]
            for env_path in env_paths:
                if os.path.exists(env_path):
                    try:
                        with open(env_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for line in content.split('\n'):
                                line = line.strip()
                                if line and 'GROQ_API_KEY' in line and '=' in line:
                                    parts = line.split('=', 1)
                                    if len(parts) == 2:
                                        api_key = parts[1].strip()
                                        break
                        if api_key:
                            break
                    except Exception as e:
                        continue
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Get a free key at https://console.groq.com/")
        
        # Initialize Groq client with OpenAI-compatible interface
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            http_client=None  # Avoid proxy issues
        )
        self.model_name = "llama-3.3-70b-versatile"  # Updated to latest model per Groq docs
    
    def generate_post(
        self,
        company: CompanyInfo,
        persona: Persona,
        subreddit: str,
        query: str,
        keywords: Optional[List[str]] = None,
        existing_posts: Optional[List[Post]] = None
    ) -> dict:
        """
        Generate a natural Reddit post based on company info, persona, and query.
        
        Args:
            company: Company information
            persona: Persona creating the post
            subreddit: Target subreddit
            query: ChatGPT query/topic to target
            existing_posts: Existing posts to avoid topic overlap
            
        Returns:
            dict with 'title' and 'content'
        """
        # Build context about existing posts to avoid overlap
        overlap_context = ""
        if existing_posts:
            recent_topics = [p.title for p in existing_posts[-3:]]
            overlap_context = f"\n\nRecent post topics to avoid duplicating: {', '.join(recent_topics)}"
        
        # Build persona context
        persona_context = f"""You are {persona.name} (Reddit username: {persona.username}), a {persona.role} with the following characteristics:
- Voice: {persona.voice}
- Interests: {', '.join(persona.interests)}
- Posting Style: {persona.posting_style}"""
        
        if persona.backstory:
            persona_context += f"\n\nYour background: {persona.backstory[:500]}..."  # Truncate if too long
        
        keyword_context = ""
        if keywords:
            keyword_context = f"\n\nTarget keywords to naturally incorporate: {', '.join(keywords)}"
        
        prompt = f"""{persona_context}

You are posting in r/{subreddit} about: {query}{keyword_context}

Context about your domain (DO NOT directly promote, just use for context):
- Company: {company.name} ({company.description})
- Domain: {company.domain}
- Target Audience: {', '.join(company.target_audience)}

Create a natural, engaging Reddit post that:
1. Sounds like a real person asking a question or sharing an experience
2. Is valuable to the community (not promotional)
3. Relates to the topic: {query}
4. Could naturally lead to discussions about tools/solutions in this space
5. Is NOT an obvious advertisement
6. Feels authentic and human-written
7. Write in YOUR voice as {persona.name} - use your posting style naturally
8. DO NOT use generic phrases like "I'm looking for recommendations" - instead ask questions or share experiences in your authentic voice{overlap_context}

Return ONLY a JSON object with this exact structure:
{{
    "title": "Your post title (engaging, question-based)",
    "content": "Your post content (2-4 sentences, natural conversation starter)"
}}

Do not include any markdown formatting, just the raw JSON."""

        try:
            # Add instruction to return JSON only - be very explicit
            full_prompt = prompt + """

CRITICAL INSTRUCTIONS:
- Return ONLY a valid JSON object
- No markdown code blocks (no ```json or ```)
- No explanations before or after
- No newlines inside string values
- Keep all text on single lines within the JSON strings
- Example format:
{"title": "Your engaging question here", "content": "Your natural post content here in one paragraph"}

Return the JSON now:"""
            
            # Generate content
            print(f"🔵 Generating post: {persona.name} → r/{subreddit}")
            
            try:
                # Call Groq API using OpenAI-compatible interface
                print(f"\n{'='*80}")
                print(f"🔵 CALLING GROQ API FOR POST")
                print(f"  Model: {self.model_name}")
                print(f"  Persona: {persona.name} ({persona.username})")
                print(f"  Subreddit: r/{subreddit}")
                print(f"  Query: {query}")
                print(f"{'='*80}\n")
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that generates natural, authentic Reddit posts. Always return valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": full_prompt
                        }
                    ],
                    temperature=0.9,
                    max_completion_tokens=600  # Using max_completion_tokens instead of deprecated max_tokens
                )
                
                # Extract content from response
                content = response.choices[0].message.content.strip()
                
                print(f"✅ Groq response received ({len(content)} chars)")
                print(f"   Content preview: {content[:150]}...\n")
                
            except Exception as api_err:
                # Handle errors
                error_str = str(api_err)
                print(f"\n{'='*80}")
                print(f"ERROR: Groq API call failed!")
                print(f"  Error: {api_err}")
                
                # Check for common error types
                if "401" in error_str or "Unauthorized" in error_str:
                    print(f"  🔧 SOLUTION: Check your GROQ_API_KEY in .env file")
                    print(f"  Get a free key at: https://console.groq.com/")
                elif "429" in error_str or "rate limit" in error_str.lower():
                    print(f"  ⚠️  Rate limit hit. Groq has generous free limits, try again in a moment.")
                elif "403" in error_str or "Forbidden" in error_str:
                    print(f"  🔧 SOLUTION: Check your API key permissions at https://console.groq.com/")
                
                print(f"{'='*80}\n")
                raise
            
            # Content extracted successfully
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                parts = content.split("```")
                if len(parts) > 1:
                    content = parts[1]
                    if content.startswith("json"):
                        content = content[4:]
            content = content.strip()
            
            # Try to extract JSON if wrapped in text
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                content = content[start:end]
            
            # Use regex to extract title and content directly if JSON parsing fails
            # This handles cases where Grok returns malformed JSON with newlines
            try:
                result = json.loads(content)
                # JSON parsed successfully
            except json.JSONDecodeError as json_err:
                print(f"⚠️  JSON parse failed, trying alternative extraction...")
                # Try to extract using regex patterns
                title_pattern = r'"title"\s*:\s*"([^"]+)"'
                content_pattern = r'"content"\s*:\s*"([^"]+)"'
                
                # Try single-line extraction first
                title_match = re.search(title_pattern, content.replace('\n', ' '))
                content_match = re.search(content_pattern, content.replace('\n', ' '))
                
                if title_match and content_match:
                    result = {
                        "title": title_match.group(1),
                        "content": content_match.group(1)
                    }
                else:
                    # Try multi-line extraction - look for title: and content: patterns
                    title_pattern_alt = r'"title"\s*:\s*"([^"]*(?:"[^"]*")*[^"]*)"'
                    content_pattern_alt = r'"content"\s*:\s*"([^"]*(?:"[^"]*")*[^"]*)"'
                    
                    # Try to find title and content even with newlines
                    lines = content.split('\n')
                    title_parts = []
                    content_parts = []
                    in_title = False
                    in_content = False
                    
                    for line in lines:
                        if '"title"' in line and ':' in line:
                            in_title = True
                            # Extract the part after :
                            if ':' in line:
                                title_part = line.split(':', 1)[1].strip()
                                if title_part.startswith('"'):
                                    title_parts.append(title_part)
                        elif '"content"' in line and ':' in line:
                            in_content = True
                            in_title = False
                            if ':' in line:
                                content_part = line.split(':', 1)[1].strip()
                                if content_part.startswith('"'):
                                    content_parts.append(content_part)
                        elif in_title and line.strip():
                            title_parts.append(line.strip())
                        elif in_content and line.strip():
                            content_parts.append(line.strip())
                        elif '}' in line:
                            in_title = False
                            in_content = False
                    
                    # Reconstruct title and content
                    if title_parts:
                        title_str = ' '.join(title_parts).strip()
                        # Remove quotes if present
                        if title_str.startswith('"') and title_str.endswith('"'):
                            title_str = title_str[1:-1]
                        elif title_str.startswith('"'):
                            title_str = title_str[1:]
                        if title_str.endswith(','):
                            title_str = title_str[:-1].strip()
                        if title_str.endswith('"'):
                            title_str = title_str[:-1]
                    else:
                        title_str = ""
                    
                    if content_parts:
                        content_str = ' '.join(content_parts).strip()
                        # Remove quotes if present
                        if content_str.startswith('"') and content_str.endswith('"'):
                            content_str = content_str[1:-1]
                        elif content_str.startswith('"'):
                            content_str = content_str[1:]
                        if content_str.endswith(','):
                            content_str = content_str[:-1].strip()
                        if content_str.endswith('"'):
                            content_str = content_str[:-1]
                    else:
                        content_str = ""
                    
                    if title_str and content_str:
                        result = {
                            "title": title_str,
                            "content": content_str
                        }
                    else:
                        raise ValueError("Could not extract title and content from response")
            title = result.get("title", "").strip()
            post_content = result.get("content", "").strip()
            
            # Validate we got actual content
            if title and post_content and len(title) > 5 and len(post_content) > 10:
                return {
                    "title": title,
                    "content": post_content
                }
            else:
                raise ValueError("Generated content too short or empty")
                
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract title and content from text
            print(f"JSON parsing error: {e}")
            print(f"Response was: {content[:300]}")
            
            # Try to extract title and content from the response text
            title_match = None
            content_match = None
            
            # Look for patterns like "title": "..." or Title: ...
            import re
            title_patterns = [
                r'"title"\s*:\s*"([^"]+)"',
                r'Title:\s*(.+)',
                r'title:\s*(.+)',
            ]
            for pattern in title_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    title_match = match.group(1).strip()
                    break
            
            content_patterns = [
                r'"content"\s*:\s*"([^"]+)"',
                r'Content:\s*(.+)',
            ]
            for pattern in content_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    content_match = match.group(1).strip()
                    break
            
            if title_match and content_match:
                return {
                    "title": title_match,
                    "content": content_match
                }
            
            # Last resort fallback
            raise ValueError("Could not extract valid content from response")
            
        except Exception as e:
            # Log the full error for debugging
            import traceback
            print(f"\n{'='*80}")
            print(f"❌ CRITICAL: Groq API failed - NO CONTENT GENERATED")
            print(f"  Error: {e}")
            print(f"  This means Groq is NOT working!")
            print(f"  Check the error above for details.")
            print(f"{'='*80}\n")
            traceback.print_exc()
            
            # NO FALLBACK - Let the error propagate so it's clear Groq isn't working
            raise Exception(f"Groq API failed: {e}. No content generated. Check your GROQ_API_KEY and API connection.")
    
    def generate_reply(
        self,
        company: CompanyInfo,
        persona: Persona,
        parent_post: Post,
        thread_posts: List[Post],
        subreddit: str
    ) -> str:
        """
        Generate a natural reply to a post.
        
        Args:
            company: Company information
            persona: Persona creating the reply
            parent_post: The post being replied to
            thread_posts: All posts in this thread (to avoid repetition)
            subreddit: Target subreddit
            
        Returns:
            Reply content string
        """
        thread_context = ""
        if thread_posts:
            thread_context = "\n\nExisting replies in this thread:\n"
            for tp in thread_posts:
                if tp.content_type == ContentType.REPLY:
                    thread_context += f"- {tp.content}\n"
        
        prompt = f"""You are {persona.name}, a {persona.role} with the following characteristics:
- Voice: {persona.voice}
- Interests: {', '.join(persona.interests)}
- Posting Style: {persona.posting_style}

You are replying to this post in r/{subreddit}:

Title: {parent_post.title}
Content: {parent_post.content}
{thread_context}

Context about your domain (use subtly, DO NOT directly promote):
- Company: {company.name} ({company.description})
- Domain: {company.domain}

Create a natural, helpful reply that:
1. Adds genuine value to the conversation
2. Sounds authentic and human-written
3. Could naturally mention tools/solutions in this space (but subtly)
4. Is NOT an obvious advertisement
5. Responds directly to what was asked/shared
6. Feels like a real person contributing to the discussion

Return ONLY the reply text (2-4 sentences), no JSON, no markdown, just the plain text reply."""

        # Generate reply
        reply_text = None
        
        try:
            full_prompt = prompt + "\n\nIMPORTANT: Return ONLY the reply text, no JSON, no markdown, no explanations, just the plain text reply."
            
            print(f"🔵 Generating reply: {persona.name} → r/{subreddit}")
            
            # Call Groq API using OpenAI-compatible interface
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates natural, authentic Reddit replies. Return only the reply text, no formatting."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                temperature=0.8,
                max_completion_tokens=300  # Using max_completion_tokens instead of deprecated max_tokens
            )
            
            # Extract reply from response
            reply_text = response.choices[0].message.content.strip()
            
            print(f"✅ Groq reply received ({len(reply_text)} chars)")
            print(f"   Reply preview: {reply_text[:100]}...\n")
            
        except Exception as api_err:
            # Error - log it clearly, no fallback
            import traceback
            print(f"\n{'='*80}")
            print(f"❌ CRITICAL: Groq API failed for reply")
            print(f"  Error: {api_err}")
            print(f"  This means Groq is NOT working!")
            print(f"{'='*80}\n")
            traceback.print_exc()
            reply_text = None
        
        # Clean up the reply (remove any markdown or extra formatting)
        if reply_text:
            if reply_text.startswith('"') and reply_text.endswith('"'):
                reply_text = reply_text[1:-1]
            if reply_text.startswith("'") and reply_text.endswith("'"):
                reply_text = reply_text[1:-1]
            
            # Validate we got actual content
            if reply_text and len(reply_text) > 10:
                return reply_text
        
        # NO FALLBACK - If API fails, return None so it's clear Groq isn't working
        print(f"\n{'='*80}")
        print(f"❌ CRITICAL: Groq API failed for reply - NO REPLY GENERATED")
        print(f"  This means Groq is NOT working!")
        print(f"  Check error messages above for details.")
        print(f"{'='*80}\n")
        
        # Return None instead of fallback - this will show as empty/missing in the calendar
        return None

