# Reddit Mastermind - Example Walkthrough

## Example: SlideForge Content Calendar Generation

### INPUT DATA

#### Company Info (SlideForge)

```
Name: SlideForge
Website: slideforge.ai
Description: AI-powered presentation tool that turns outlines into polished slide decks
Target Audience: Operators, consultants, founders, sales teams, educators
Key Features:
  - Converts notes to professional slides
  - Supports PowerPoint, Google Slides, PDF export
  - Branded templates
  - API for integrations
```

#### Personas (2+)

```
Persona 1: "Alex - Product Manager"
  - Role: Product Manager at a tech startup
  - Voice: Professional, strategic, data-driven
  - Interests: Product roadmaps, user experience, growth metrics
  - Posting Style: Thoughtful, asks questions, shares experiences

Persona 2: "Jordan - Startup Founder"
  - Role: Founder of a SaaS company
  - Voice: Enthusiastic, practical, problem-solving focused
  - Interests: Startup growth, sales, team building
  - Posting Style: Direct, shares real examples, offers help
```

#### Subreddits

```
- r/productmanagement
- r/startups
- r/sales
- r/entrepreneur
- r/SaaS
```

#### ChatGPT Queries to Target

```
- "How to create better product presentations"
- "Best tools for startup pitch decks"
- "Tips for sales team presentations"
- "How to save time on slide creation"
```

#### Number of Posts per Week

```
3 posts per week
```

---

## THE PROBLEM - Step by Step

### Step 1: Content Generation Challenge

**What we need:**

- Generate 3 original posts that feel natural
- Each post should relate to SlideForge's domain but NOT be obvious ads
- Posts should be based on the ChatGPT queries

**Example of a GOOD post:**

```
Title: "How do you handle last-minute presentation requests?"
Subreddit: r/productmanagement
Content: "I'm constantly getting asked to create product updates
on short notice. What's your process for quickly putting together
professional-looking slides? Do you have templates, or do you
build from scratch each time?"
```

**Example of a BAD post (too obvious):**

```
Title: "Use SlideForge for your presentations!"
Content: "SlideForge is the best tool for creating presentations..."
```

### Step 2: Persona Reply Strategy

**What we need:**

- After someone posts, have our personas reply naturally
- Replies should add value, not just promote
- Different personas should have different perspectives

**Example conversation flow:**

```
Day 1, Monday 10am:
- Alex posts: "How do you handle last-minute presentation requests?"
  (in r/productmanagement)

Day 1, Monday 2pm:
- Jordan replies: "I used to struggle with this too. I've started
  keeping a library of templates for common scenarios. What types
  of presentations do you need most often?"

Day 2, Tuesday 11am:
- Alex replies to Jordan: "Mostly product updates and roadmap
  reviews. The challenge is making them look polished without
  spending hours on design..."

Day 3, Wednesday 3pm:
- Jordan replies: "Have you tried any tools that help with this?
  I've been experimenting with AI-powered ones that can turn
  rough notes into something presentable pretty quickly."
```

### Step 3: Distribution Challenge

**What we need:**

- Spread 3 posts across the week
- Don't post too much in the same subreddit
- Space out replies naturally (not all at once)
- Avoid awkward patterns (e.g., same persona always replying first)

**BAD Distribution:**

```
Monday: Post in r/productmanagement
Monday: Post in r/productmanagement (TOO SOON!)
Monday: Post in r/productmanagement (SPAM!)
```

**GOOD Distribution:**

```
Monday 10am: Post in r/productmanagement
Tuesday 2pm: Post in r/startups
Thursday 11am: Post in r/sales
```

### Step 4: Quality Checks Needed

**Edge cases to handle:**

1. **Overposting:** Don't post more than 1-2 times per week in same subreddit
2. **Topic Overlap:** Don't post similar topics on the same day
3. **Persona Conflicts:** Don't have personas reply to each other awkwardly
4. **Natural Timing:** Replies should come hours/days after posts, not minutes

---

## EXPECTED OUTPUT - Content Calendar

### Week 1 Calendar

| Date     | Time  | Type   | Persona             | Subreddit                                               | Title                                                    | Content Preview |
| -------- | ----- | ------ | ------------------- | ------------------------------------------------------- | -------------------------------------------------------- | --------------- |
| Mon 10am | Post  | Alex   | r/productmanagement | "How do you handle last-minute presentation requests?"  | "I'm constantly getting asked..."                        |
| Mon 2pm  | Reply | Jordan | r/productmanagement | (Reply to Alex's post)                                  | "I used to struggle with this too..."                    |
| Tue 11am | Reply | Alex   | r/productmanagement | (Reply to Jordan)                                       | "Mostly product updates..."                              |
| Tue 2pm  | Post  | Jordan | r/startups          | "What's your process for pitch deck creation?"          | "As a founder, I spend way too much time..."             |
| Wed 3pm  | Reply | Alex   | r/startups          | (Reply to Jordan's post)                                | "Have you tried templating your common slides?"          |
| Thu 11am | Post  | Alex   | r/sales             | "Sales team: how do you keep presentations consistent?" | "Our sales team creates dozens of decks..."              |
| Thu 4pm  | Reply | Jordan | r/sales             | (Reply to Alex's post)                                  | "We solved this by creating a brand template library..." |

---

## THE ALGORITHM - How It Works

### Phase 1: Content Planning

1. Take 3 posts per week requirement
2. Distribute across subreddits (max 1-2 per subreddit per week)
3. Assign personas to posts (rotate for variety)
4. Generate post topics from ChatGPT queries + company context

### Phase 2: Post Generation

1. For each scheduled post:
   - Use persona voice + company domain knowledge
   - Generate natural question/discussion starter
   - Ensure it's valuable, not promotional

### Phase 3: Reply Strategy

1. For each post, plan 1-2 strategic replies:
   - Different persona replies
   - Natural time delay (2-24 hours)
   - Adds value, subtly relates to company domain
   - Can mention tools/solutions naturally

### Phase 4: Quality Validation

1. Check subreddit distribution (no overposting)
2. Check topic diversity (no overlap)
3. Check persona rotation (not always same pattern)
4. Check timing (natural conversation flow)

### Phase 5: Calendar Generation

1. Output structured calendar with all posts/replies
2. Include metadata: persona, subreddit, timing, content
3. Make it easy to review and export

---

## CHALLENGES TO SOLVE

1. **Natural Language:** Posts must sound human, not AI-generated
2. **Strategic Promotion:** Mention company/tool naturally, not as ads
3. **Distribution Logic:** Smart subreddit and timing distribution
4. **Persona Consistency:** Each persona maintains distinct voice
5. **Conversation Flow:** Replies feel like real discussions
6. **Edge Cases:** Handle all the "what if" scenarios

---

## NEXT STEPS FOR IMPLEMENTATION

1. Set up project structure
2. Create data models (Company, Persona, Calendar, Post, Reply)
3. Build content generation engine
4. Build scheduling/distribution algorithm
5. Build quality validation system
6. Create web interface for input/output
7. Add testing framework
