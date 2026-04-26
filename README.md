# AI-Powered Skill Assessment & Personalised Learning Plan Agent

An interactive Streamlit application that evaluates a candidate's real skill proficiency based on a Job Description (JD) and Resume. It extracts the intersection of required and possessed skills, runs a live technical assessment, and creates a tailored technical learning roadmap.

## 🚀 Live Demo
[Click here for Live Demo](https://ai-skill-assessment-agent-a8h3abfkkl49mdmsbhybny.streamlit.app/)
(Or "Run locally using instructions below")

## 🎯 Problem
Resumes often misrepresent actual skill levels. This agent evaluates real proficiency instead.

## 💡 Solution
An AI agent that:
- Extracts skills from JD + Resume
- Conducts interactive assessment
- Evaluates real proficiency
- Generates personalized learning roadmap

---

## 🏗️ Architecture Flow

```
Input (JD + PDF Resume) 
      ↓
Skill Extraction Engine (Gemini API) 
      ↓
Skill Gap Analyzer (Python logic)
      ↓
Mode Selection (Quick vs Full Test)
      ↓
Assessment Q&A Agent (Gemini API iteratively)
      ↓
Skill Scoring & Aggregation
      ↓
Executive Summary & Learning Plan Generator (Gemini API)
      ↓
UI Output (Streamlit with Downloadable Exports)
```

---

## ✨ Features

- **Robust Input Handling**: Upload your resume directly as a PDF (via PyPDF2) or paste raw text. You can also use the included "Sample Data" for a quick 1-click demonstration!
- **Selective Assessment**: Choose whether you want a comprehensive Full Test of all claimed skills, or a Quick Test that verifies just the top 3 critical traits.
- **Granular Skill Scoring**: Answers are evaluated individually via AI (using explicit `Pydantic` schemas for structured evaluations). The results are aggregated into a final status logic of *Advanced*, *Intermediate*, or *Beginner*.
- **Executive Summaries**: Instead of just displaying raw grades, the AI computes a short, professional breakdown outlining key strengths and critical weaknesses.
- **Context-Aware Learning Plan**: A custom roadmap dictating estimated time, exact practical actions, and targeted reading resources focusing purely on the missing skills and weak areas.
- **Exporting**: Download the final learning plan directly as a JSON file or straightforward text file.

---

## 🚀 Setup Instructions

1. **Clone the repository** (if applicable) or navigate to the directory.
   ```bash
   cd d:/ai-skill-agent
   ```

2. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   - Create a `.env` file (`.env` placeholder is provided).
   - Add your Gemini API key:
     ```env
     GEMINI_API_KEY=your_real_api_key_here
     ```

4. **Run the App**
   ```bash
   streamlit run app.py
   ```

## 🎯 Demoing
Simply launch the application and hit **Use Sample Data** on the first screen to populate a mock Data Analyst job description and candidate profile. Proceed to take the **⚡ Quick Test** to experience the agent in action!
