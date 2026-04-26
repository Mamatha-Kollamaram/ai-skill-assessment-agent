import streamlit as st
import utils
from dotenv import load_dotenv
import time
import json

load_dotenv()

st.set_page_config(page_title="AI Skill Agent", page_icon="🤖", layout="wide")

# Custom CSS for UI Polish
st.markdown("""
<style>
.stApp {
    background-color: #f8f9fa;
}
h1, h2, h3 {
    color: #2b2d42;
    font-family: 'Inter', sans-serif;
}
.skill-tag {
    display: inline-block;
    padding: 0.3em 0.8em;
    margin: 0.2em;
    border-radius: 15px;
    background-color: #e0fbfc;
    color: #3d5a80;
    font-weight: 600;
    font-size: 0.9em;
}
.skill-tag.missing {
    background-color: #ffd6d6;
    color: #d90429;
}
.skill-tag.matched {
    background-color: #d8f3dc;
    color: #2d6a4f;
}
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "step" not in st.session_state:
    st.session_state.step = 1
if "jd_sample" not in st.session_state:
    st.session_state.jd_sample = ""
if "resume_sample" not in st.session_state:
    st.session_state.resume_sample = ""
if "extraction" not in st.session_state:
    st.session_state.extraction = None
if "gap" not in st.session_state:
    st.session_state.gap = None
if "selected_skills" not in st.session_state:
    st.session_state.selected_skills = []
if "current_skill_idx" not in st.session_state:
    st.session_state.current_skill_idx = 0
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 1
if "questions" not in st.session_state:
    st.session_state.questions = {}
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "evaluations" not in st.session_state:
    st.session_state.evaluations = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "learning_plan" not in st.session_state:
    st.session_state.learning_plan = None
if "why_this_plan" not in st.session_state:
    st.session_state.why_this_plan = ""
if "overall_goal" not in st.session_state:
    st.session_state.overall_goal = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

st.title("🤖 AI-Powered Skill Assessment Agent")
st.markdown("---")

steps_dict = {
    1: "Input",
    2: "Analysis",
    3: "Assessment",
    4: "Results"
}
st.caption(f"**Step {st.session_state.step}/4 — {steps_dict.get(st.session_state.step, '')}**")

# Section 1: Inputs
if st.session_state.step == 1:
    st.subheader("1. Provide Job Details and Candidate Resume")
    
    # Sample Input Button
    if st.button("Use Sample Data"):
        st.session_state.jd_sample = "Data Analyst required. Must know Python, SQL, Machine Learning, and Data Visualization tools like Tableau."
        st.session_state.resume_sample = "Experienced professional. Skilled in Python, Excel, SQL, Pandas, and basic statistics."
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        jd_input = st.text_area("Job Description", height=300, value=st.session_state.jd_sample, placeholder="Paste JD here...")
    with col2:
        st.write("Candidate Resume")
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        resume_text_area = st.text_area("Or paste resume plain text", height=200, value=st.session_state.resume_sample, placeholder="Paste resume here...")
        
    if st.button("Start Analysis 🚀", type="primary"):
        resume_content = resume_text_area
        
        # Parse PDF if uploaded
        if uploaded_file:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pdf_text += text
                if pdf_text.strip():
                    resume_content = pdf_text
            except Exception as e:
                st.warning("Could not read PDF properly. Proceeding with pasted text.")

        if jd_input and resume_content:
            with st.spinner("Analyzing JD and Resume..."):
                ext_res = utils.extract_skills(jd_input, resume_content)
                
                if "error" in ext_res:
                    st.error(ext_res["error"])
                elif not ext_res.get('required_skills'):
                    st.error("Could not extract skills. Please try again.")
                else:
                    st.session_state.extraction = ext_res
                    
                    matched, missing = utils.analyze_gap(ext_res['required_skills'], ext_res['candidate_skills'])
                    st.session_state.gap = {"matched": matched, "missing": missing}
                    
                    st.session_state.step = 2
                    st.rerun()
        else:
            st.warning("Please provide both Job Description and Resume data.")

# Section 2: Gap Analysis & Mode Select
if st.session_state.step >= 2:
    st.subheader("📊 2. Skill Gap Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    matched = st.session_state.gap['matched']
    missing = st.session_state.gap['missing']
    
    with col1:
        st.markdown("**Required Skills:**")
        st.markdown(" ".join([f"<span class='skill-tag'>{s}</span>" for s in st.session_state.extraction['required_skills']]), unsafe_allow_html=True)
        
    with col2:
        st.markdown("**Matched Skills (To Assess):**")
        if matched:
            st.markdown(" ".join([f"<span class='skill-tag matched'>✓ {s}</span>" for s in matched]), unsafe_allow_html=True)
        else:
            st.info("No overlapping skills found to assess.")
            
    with col3:
        st.markdown("**Missing Skills:**")
        if missing:
             st.markdown(" ".join([f"<span class='skill-tag missing'>✗ {s}</span>" for s in missing]), unsafe_allow_html=True)
        else:
             st.success("Candidate possesses all required skills!")
             
    st.markdown("---")
    
    if st.session_state.step == 2:
        if matched:
            mode = st.radio(
                "Choose Assessment Mode:",
                ["⚡ Quick Test (1–2 key skills)", "🧠 Full Test (all matched skills)"]
            )
            if st.button("Begin Assessment 🎤", type="primary"):
                if "⚡ Quick Test" in mode:
                    st.session_state.selected_skills = matched[:2]
                else:
                    st.session_state.selected_skills = matched
                    
                st.session_state.step = 3
                st.session_state.chat_history = []
                st.rerun()
        else:
            if st.button("Skip to Learning Plan 📚", type="primary"):
                 st.session_state.step = 4
                 st.rerun()

# Section 3: Interactive Assessment
if st.session_state.step == 3:
    st.subheader("🎤 3. Interactive Assessment")
    
    targets = st.session_state.selected_skills
    
    if targets:
        total_questions = len(targets) * 2
        completed = (st.session_state.current_skill_idx * 2) + (st.session_state.current_question_idx - 1)
        progress = completed / total_questions if total_questions > 0 else 1.0
        st.progress(min(1.0, max(0.0, progress)))
    
    if st.session_state.current_skill_idx < len(targets):
        current_skill = targets[st.session_state.current_skill_idx]
        
        st.write(f"### Assessing Skill: **{current_skill}** (Question {st.session_state.current_question_idx}/2)")
        
        # Display chat history for current skill
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        # Check if we need to evaluate
        answers_for_skill = st.session_state.answers.get(current_skill, [])
        if len(answers_for_skill) == 2 and current_skill not in st.session_state.evaluations:
            with st.spinner("Evaluating your answers for this skill..."):
                eval_res = utils.evaluate_answers(current_skill, answers_for_skill)
                
                if "error" in eval_res:
                    st.error(eval_res["error"])
                    if st.button("Retry Evaluation"):
                        st.rerun()
                else:
                    st.session_state.evaluations[current_skill] = [
                        {"eval": eval_res}
                    ]
                    st.session_state.current_skill_idx += 1
                    st.session_state.current_question_idx = 1
                    st.session_state.chat_history = [] # Reset chat for next skill
                    st.rerun()
        else:
            # Generate new question if needed
            if len(st.session_state.chat_history) % 2 == 0:
                 # Check if we already have questions for this skill
                 if current_skill not in st.session_state.questions:
                     with st.spinner("Generating questions for this skill..."):
                         q_list = utils.generate_questions(current_skill)
                         # Handle error cases
                         if q_list and isinstance(q_list[0], str) and q_list[0].startswith("Error"):
                             st.error(q_list[0])
                             if st.button("Retry Generating Question"):
                                 st.rerun()
                         else:
                             st.session_state.questions[current_skill] = q_list
                             st.session_state.answers[current_skill] = []
                 
                 if current_skill in st.session_state.questions:
                     # Fetch the current question (index is 1-based)
                     q_idx = st.session_state.current_question_idx - 1
                     q_text = st.session_state.questions[current_skill][q_idx]
                     st.session_state.chat_history.append({"role": "assistant", "content": q_text, "type": "question"})
                     st.rerun()
                     
            # Await answer
            if current_skill in st.session_state.questions and len(answers_for_skill) < 2:
                if answer := st.chat_input("Type your answer here..."):
                    st.session_state.chat_history.append({"role": "user", "content": answer})
                    
                    # Store answer
                    q_idx = st.session_state.current_question_idx - 1
                    question_text = st.session_state.questions[current_skill][q_idx]
                    st.session_state.answers[current_skill].append({
                        "question": question_text,
                        "answer": answer
                    })
                    
                    # Move to next question or trigger evaluation on next rerun
                    if st.session_state.current_question_idx < 2:
                        st.session_state.current_question_idx += 1
                    st.rerun()
                
    else:
        st.success("All assessments complete!")
        if st.button("View Final Report & Learning Plan 📄", type="primary"):
            st.session_state.step = 4
            st.rerun()

# Section 4 & 5: Report and Learning Plan
if st.session_state.step == 4:
    st.subheader("📈 3. Final Skill Evaluation")
    
    final_levels = {}
    
    if st.session_state.evaluations:
        # Precompute final levels
        for skill, evals in st.session_state.evaluations.items():
            final_levels[skill] = utils.get_final_level(evals)

        # Generate summary specifically if not done
        if not st.session_state.summary:
            with st.spinner("Drafting executive summary..."):
                 summary_res = utils.generate_summary(final_levels)
                 if summary_res.startswith("Error"):
                     st.error(summary_res)
                     if st.button("Retry Summary Generation"):
                         st.rerun()
                 else:
                     st.session_state.summary = summary_res
                     st.rerun()

        if st.session_state.summary:
             st.info(f"**Executive Summary:**\n{st.session_state.summary}")

        for skill, evals in st.session_state.evaluations.items():
            with st.expander(f"Review Details: {skill}"):
                 level = final_levels[skill]
                 st.markdown(f"### {skill}: {level}")
                 if level == "Advanced":
                     st.success("Strong proficiency")
                 elif level == "Intermediate":
                     st.warning("Moderate proficiency")
                 else:
                     st.error("Needs improvement")
                 
                 st.markdown("---")
                 
                 # Display QA pairs
                 qa_pairs = st.session_state.answers.get(skill, [])
                 for i, pair in enumerate(qa_pairs):
                     st.write(f"**Q{i+1}:**")
                     st.info(pair['question'])
                     st.write("**Answer:**")
                     st.info(pair['answer'])
                     
                 # Display the reasoning from the single combined evaluation
                 reasoning = evals[0].get('eval', {}).get('reasoning', '')
                 st.write(f"**Overall Assessment Reasoning:** {reasoning}")
    else:
        st.info("No skills were assessed.")

    st.markdown("---")
    st.subheader("📚 4. Personalized Learning Roadmap")
    
    if st.session_state.learning_plan is None:
        with st.spinner("Generating learning plan..."):
             plan_res = utils.generate_learning_plan(final_levels, st.session_state.gap['missing'])
             if "error" in plan_res:
                 st.error(plan_res["error"])
                 if st.button("Retry Learning Plan Generation"):
                     st.rerun()
             else:
                 st.session_state.learning_plan = plan_res.get('roadmap', {})
                 st.session_state.why_this_plan = plan_res.get('why_this_plan', '')
                 st.session_state.overall_goal = plan_res.get('overall_goal', '')
                 st.rerun()
             
    if st.session_state.learning_plan:
         if st.session_state.overall_goal:
             st.success(f"🎯 **Overall Goal:** {st.session_state.overall_goal}")
             
         st.markdown(f"### 🤔 Why this plan?")
         st.write(st.session_state.why_this_plan)
         st.markdown("---")

         for skill, details in st.session_state.learning_plan.items():
              with st.container():
                   st.markdown(f"#### 🛤️ Roadmap for: **{skill}**")
                   col_time, col_rest = st.columns([1, 4])
                   with col_time:
                       st.info(f"⏳ **Est. Time**\n{details.get('time', 'N/A')}")
                   with col_rest:
                       st.markdown("**Action Plan:**")
                       for step in details.get('plan', []):
                           st.markdown(f"- {step}")
                       st.markdown("**Resources:**")
                       for res in details.get('resources', []):
                           st.markdown(f"- 📖 {res}")
                   st.write("---")

         dl_col1, dl_col2 = st.columns(2)
         with dl_col1:
             st.download_button(
                 label="Download Plan as JSON",
                 data=json.dumps(st.session_state.learning_plan, indent=2),
                 file_name="learning_plan.json",
                 mime="application/json"
             )
         with dl_col2:
             # Make a pretty text string for download
             text_dl = "Personalized Learning Plan\n" + "="*30 + "\n\n"
             text_dl += "Why this plan?\n" + st.session_state.why_this_plan + "\n\n"
             for sk, det in st.session_state.learning_plan.items():
                 text_dl += f"Skill: {sk}\n"
                 text_dl += f"Time: {det.get('time')}\n"
                 text_dl += "Plan Steps:\n" + "".join([f" - {x}\n" for x in det.get('plan', [])])
                 text_dl += "Resources:\n" + "".join([f" - {x}\n" for x in det.get('resources', [])])
                 text_dl += "-"*20 + "\n"
             st.download_button(
                 label="Download as Text",
                 data=text_dl,
                 file_name="learning_plan.txt"
             )

    st.markdown("---")
    if st.button("🔄 Start Over", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

