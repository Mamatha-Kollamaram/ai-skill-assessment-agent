SKILL_EXTRACTION_PROMPT = """
You are an expert technical recruiter and HR software.
Extract the technical skills required from the following Job Description (JD) and the candidate's skills from the following Resume.

Job Description:
{jd}

Resume:
{resume}

Return the results matching the required JSON schema.
"""

QUESTION_GENERATION_PROMPT = """
You are a senior technical interviewer. We are assessing a candidate's real-world proficiency in the following skill: '{skill}'

Generate 2 practical, open-ended questions for this skill.
Question 1 should be a fundamental but practical question.
Question 2 should be an applied scenario or debugging question.

Return EXACTLY 2 questions as a JSON array of strings.
Example:
["Question 1 text...", "Question 2 text..."]

Do NOT return more or fewer.
Do NOT provide options or answers.
"""

EVALUATION_PROMPT = """
You are an expert technical assessor grading a candidate's proficiency.
Skill: {skill}

Evaluate the candidate based on the following:

{qa_context}

Evaluate their answers for correctness, depth, and practical understanding.
Return JSON:
{{
  "level": "Beginner | Intermediate | Advanced",
  "reasoning": "..."
}}

Provide a concise reasoning (1-2 sentences) for your evaluation.
"""

SUMMARY_PROMPT = """
You are an expert career coach.

Based on the following skill levels:
{skill_levels}

Write a short 3-4 line professional summary describing:
- strengths
- weaknesses
- overall readiness

Keep it concise and insightful.
"""

LEARNING_PLAN_PROMPT = """
You are an expert career coach and technical learning mentor.
Based on the candidate's skill profile below (including strengths and gaps), generate a realistic learning roadmap for the candidate. 

Candidate's Skill Profile:
{skills_context}

Create a learning plan containing customized plans for each skill. 
Follow these guidelines to make it highly actionable and polished:
1. Titles: Make titles personalized and less generic (e.g., "SQL (Intermediate -> Advanced)" instead of just "SQL").
2. Time Estimates: Include an assumption context for time estimates (e.g., "2 weeks (assuming 1-2 hours/day)").
3. Action Plan: Emphasize project-based learning. Add specific real-world mini-projects (e.g., "Build a mini project: Analyze sales dataset and create SQL + Tableau dashboard").
4. Resources: Add rich context to resources instead of just names (e.g., "LeetCode Database Challenges – practice real interview-level SQL problems").

Include an "overall_goal" string that ties everything together (e.g., "Transition from current skillset -> Data Analyst readiness in ~3 months").
Also include a short explanation titled "Why this plan?" explaining the reasoning behind the roadmap.
"""
