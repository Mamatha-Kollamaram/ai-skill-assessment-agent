import os
import json
import time
from pydantic import BaseModel
from typing import List, Dict
from google import genai
from google.genai import types
from dotenv import load_dotenv
import prompts

# Load environment variables
load_dotenv()

# Initialize Gemini Client
client = genai.Client()
MODEL = "gemini-flash-latest"

# --- Pydantic Data Models ---
class ExtractionResult(BaseModel):
    required_skills: List[str]
    candidate_skills: List[str]

class QuestionsResult(BaseModel):
    questions: List[str]

class EvaluationResult(BaseModel):
    level: str
    reasoning: str

class LearningSkillPlan(BaseModel):
    skill: str
    time: str
    plan: List[str]
    resources: List[str]

class LearningPlanResult(BaseModel):
    overall_goal: str
    roadmap: List[LearningSkillPlan]
    why_this_plan: str

class SummaryResult(BaseModel):
    summary: str

# --- Core Functions ---

def parse_json_response(text: str):
    """Clean markdown formatting and parse JSON."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


def extract_skills(jd: str, resume: str) -> dict:
    """Extract required and candidate skills using Gemini."""
    prompt = prompts.SKILL_EXTRACTION_PROMPT.format(jd=jd, resume=resume)
    
    for _ in range(2):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractionResult,
                    temperature=0.2,
                ),
            )
            return parse_json_response(response.text)
        except Exception as e:
            print("ERROR in extract_skills:", e)
            time.sleep(2)
    return {"error": "API limit reached. Try again in a few seconds."}

def analyze_gap(required: List[str], candidate: List[str]) -> tuple:
    """Returns matched and missing skills."""
    req_set = set([s.lower().strip() for s in required])
    cand_set = set([s.lower().strip() for s in candidate])
    
    matched = []
    missing = []
    
    for req in required:
        req_l = req.lower().strip()
        if req_l in cand_set:
            matched.append(req)
        else:
            missing.append(req)
            
    return matched, missing

def generate_questions(skill: str) -> list:
    """Generates exactly 2 questions for a skill."""
    prompt = prompts.QUESTION_GENERATION_PROMPT.format(skill=skill)
    
    for _ in range(2):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=QuestionsResult,
                    temperature=0.7,
                )
            )
            questions_dict = parse_json_response(response.text)
            questions = questions_dict.get("questions", [])
            
            if len(questions) != 2:
                raise ValueError(f"Model returned {len(questions)} questions instead of 2")
                
            return questions
        except Exception as e:
            print("ERROR in generate_questions:", e)
            time.sleep(2)
    return ["Error: API limit reached. Could not generate questions.", "Please try again later."]

def evaluate_answers(skill: str, qa_pairs: List[dict]) -> dict:
    """Evaluates all candidate's answers for a skill in a single batch."""
    
    context_lines = []
    for i, pair in enumerate(qa_pairs):
        context_lines.append(f"Q{i+1}: {pair['question']}")
        context_lines.append(f"Answer{i+1}: {pair['answer']}\n")
    
    qa_context = "\n".join(context_lines)
    
    prompt = prompts.EVALUATION_PROMPT.format(skill=skill, qa_context=qa_context)
    
    for _ in range(2):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EvaluationResult,
                    temperature=0.2,
                )
            )
            return parse_json_response(response.text)
        except Exception as e:
            print("ERROR in evaluate_answers:", e)
            time.sleep(2)
    return {"error": "API limit reached. Try again in a few seconds."}

def get_final_level(evaluations: List[dict]) -> str:
    """Aggregates multiple evaluations to output a single skill level.
    Since we only have 1 evaluation per skill now, it just returns that level."""
    if not evaluations:
        return "Beginner"
        
    # In the new architecture, there's only 1 combined evaluation per skill
    return evaluations[0].get("eval", {}).get("level", "Beginner")

def generate_summary(final_levels: dict) -> str:
    """Generates a short summary text from aggregated final levels."""
    levels_text = json.dumps(final_levels, indent=2)
    prompt = prompts.SUMMARY_PROMPT.format(skill_levels=levels_text)
    
    for _ in range(2):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SummaryResult,
                    temperature=0.6,
                )
            )
            data = parse_json_response(response.text)
            return data.get("summary", "Summary generation failed.")
        except Exception as e:
            print("ERROR in generate_summary:", e)
            time.sleep(2)
    return "Error: API limit reached. Try again in a few seconds."

def generate_learning_plan(final_levels: dict, missing_skills: List[str]) -> dict:
    """Generates a learning roadmap based on missing skills and final skill levels."""
    context_lines = []
    if missing_skills:
        context_lines.append(f"Missing Skills (Not on Resume): {', '.join(missing_skills)}")
        
    for skill, level in final_levels.items():
         context_lines.append(f"{skill}: Final Assessed Level => {level}")
         
    if not context_lines:
         context_lines.append("Candidate is highly proficient. Provide an advanced/maintenance plan to keep skills sharp.")
             
    context_str = "\n".join(context_lines)
    
    prompt = prompts.LEARNING_PLAN_PROMPT.format(skills_context=context_str)
    
    for _ in range(2):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LearningPlanResult,
                    temperature=0.5,
                )
            )
            data = parse_json_response(response.text)
            if "roadmap" in data and isinstance(data["roadmap"], list):
                roadmap_dict = {}
                for item in data["roadmap"]:
                    skill_name = item.get("skill", "Unknown")
                    roadmap_dict[skill_name] = item
                data["roadmap"] = roadmap_dict
            return data
        except Exception as e:
            print("ERROR in generate_learning_plan:", e)
            time.sleep(2)
            
    return {"error": "API limit reached. Try again in a few seconds."}
