import os
import datetime

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

try:
    from crewai import Agent, Task, Crew
    CREW_AVAILABLE = True
except ImportError:
    CREW_AVAILABLE = False

# ---------- Load environment variables ----------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


# ---------- Helper: call AI model (Gemini) ----------
def call_study_agent(
    system_prompt: str,
    user_prompt: str,
    model: str = "gemini-2.0-flash",
    temperature: float = 0.7,
) -> str:
    """Generic helper for different study tasks using Gemini."""
    if not GOOGLE_API_KEY:
        return "ERROR: GOOGLE_API_KEY is not set. Please configure your .env file."

    try:
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            top_p=0.95,
            top_k=40,
            max_output_tokens=1024,
        )
        gemini_model = genai.GenerativeModel(model)
        prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
        response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config,
        )
        return (response.text or "").strip()
    except Exception as e:
        return f"Error calling model: {e}"


def call_crewai_study_agent(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Use a simple CrewAI crew to answer study questions.

    Assumes CrewAI is installed and configured via environment (e.g. OpenAI key
    or other provider) according to CrewAI's documentation.
    """
    if not CREW_AVAILABLE:
        return (
            "ERROR: CrewAI is not installed. Please ensure 'crewai' is in your "
            "environment and dependencies."
        )

    # CrewAI's default native provider usually requires OPENAI_API_KEY.
    # Check for it explicitly so we can show a clearer message instead of
    # letting CrewAI raise a low-level import/provider error.
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        return (
            "ERROR: OPENAI_API_KEY is not set. To use the CrewAI backend, "
            "add OPENAI_API_KEY to your .env file (or configure another "
            "provider according to CrewAI's documentation)."
        )

    try:
        full_context = f"{system_prompt}\n\n{user_prompt}"

        study_agent = Agent(
            role="Study Assistant",
            goal=(
                "Help students understand concepts, answer questions clearly, "
                "and give step-by-step explanations."
            ),
            backstory=(
                "You are a friendly expert tutor who adapts explanations to "
                "the student's level and focuses on clarity."
            ),
        )

        qa_task = Task(
            description=(
                "Read the study context and the student's question, then give a "
                "clear, structured explanation with examples.\n\n" + full_context
            ),
            agent=study_agent,
            expected_output=(
                "A concise but clear answer with explanations and, when helpful, "
                "step-by-step reasoning and examples."
            ),
        )

        crew = Crew(agents=[study_agent], tasks=[qa_task])
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return f"Error calling CrewAI: {e}"


# ---------- Streamlit page config ----------
st.set_page_config(
    page_title="MULTI AGENT  Personal Study Assistant",
    page_icon="📚",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Simple fade/slide-in animation for main headings */
    @keyframes fadeInDown {
        0% { opacity: 0; transform: translateY(-12px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Apply animation to all top-level headers */
    h1 {
        animation: fadeInDown 0.9s ease-in-out;
    }

    /* Subtle hover animation for metric cards */
    div[data-testid="stMetric"] {
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        border-radius: 0.75rem;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
    }

    /* Add a soft accent line under the tab headers */
    button[role="tab"] {
        transition: box-shadow 0.18s ease, transform 0.18s ease;
        border-radius: 999px !important;
    }

    button[role="tab"][aria-selected="true"] {
        box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.5),
                    0 8px 20px rgba(99, 102, 241, 0.25);
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar: global settings ----------
st.sidebar.title("📚 MULTI AGENT  Study Assistant")
st.sidebar.write("AI-powered personal study helper.")

model_choice = st.sidebar.selectbox(
    "Gemini model",
    ["gemini-2.0-flash", "gemini-2.0-pro"],
    index=0,
)

creativity = st.sidebar.slider(
    "Creativity (temperature)",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
)

study_mode = st.sidebar.selectbox(
    "Study mode",
    ["Balanced", "Exam prep", "Deep understanding"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Tips**")
st.sidebar.markdown(
    "- Use clear questions.\n"
    "- Paste your notes for summaries.\n"
    "- Generate quizzes to test yourself.\n"
    "- Add reminders to keep on track."
)

# Initialize session state for reminders
if "reminders" not in st.session_state:
    st.session_state["reminders"] = []


# ---------- Dashboard Header ----------
st.title("🎓 Personal Study Assistant")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Questions Answered", "AI-based", "Unlimited")
with col2:
    st.metric("Summaries Created", "On demand", "Fast")
with col3:
    st.metric("Quizzes Generated", "Custom", "Topic-based")
with col4:
    st.metric("Reminders Saved", len(st.session_state["reminders"]))


st.markdown("---")

# ---------- Tabs for capabilities ----------
tab_qa, tab_notes, tab_quiz, tab_reminders = st.tabs(
    ["❓ Ask Questions", "📝 Notes & Summaries", "🧠 Quizzes", "⏰ Study Reminders"]
)

# ---------- Tab 1: Q&A ----------
with tab_qa:
    st.subheader("Ask any study question")
    subject = st.text_input("Subject / Topic (optional)", placeholder="e.g., Calculus, World War II, Python")
    question = st.text_area("Your question", height=150, placeholder="Type your question here...")

    col_qa1, col_qa2 = st.columns([1, 3])
    with col_qa1:
        level = st.selectbox(
            "Level",
            ["School", "Undergraduate", "Graduate", "General"],
            index=0,
        )
    with col_qa2:
        style = st.selectbox(
            "Explanation style",
            ["Simple", "Detailed", "Step-by-step"],
            index=2,
        )

    if st.button("Get Answer", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            system_prompt = (
                "You are a helpful personal study assistant for students. "
                "Explain concepts clearly, with examples. Adapt your explanation "
                f"to a {level} student and keep the tone encouraging. "
                f"Explanation style: {style}. "
                f"Overall study mode: {study_mode}."
            )
            user_prompt = f"Subject: {subject}\nQuestion: {question}"
            with st.spinner("Thinking..."):
                answer = call_study_agent(
                    system_prompt,
                    user_prompt,
                    model=model_choice,
                    temperature=creativity,
                )
            st.markdown("### ✅ Answer")
            st.write(answer)

# ---------- Tab 2: Notes & Summaries ----------
with tab_notes:
    st.subheader("Create notes and summaries")

    mode = st.radio(
        "What do you want?",
        ["Summarize my text", "Turn topic into structured notes"],
        horizontal=True,
    )

    if mode == "Summarize my text":
        text_to_summarize = st.text_area(
            "Paste your study material / notes here",
            height=220,
            placeholder="Paste textbook pages, lecture notes, or long explanations here...",
        )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            summary_length = st.selectbox(
                "Summary length",
                ["Very short (bullet points)", "Short", "Medium", "Detailed"],
                index=1,
            )
        with col_s2:
            highlight = st.checkbox("Highlight key terms", value=True)

        if st.button("Generate Summary", type="primary"):
            if not text_to_summarize.strip():
                st.warning("Please paste some text to summarize.")
            else:
                system_prompt = (
                    "You are an AI note-taker. Summarize the input text into clear study notes.\n"
                    f"- Summary length: {summary_length}.\n"
                    f"- Highlight key terms: {'yes' if highlight else 'no'}.\n"
                    f"- Overall study mode: {study_mode}.\n"
                    "- Use headings and bullet points where helpful."
                )
                with st.spinner("Generating summary..."):
                    summary = call_study_agent(
                        system_prompt,
                        text_to_summarize,
                        model=model_choice,
                        temperature=creativity,
                    )
                st.markdown("### 📝 Summary")
                st.write(summary)

    else:  # Turn topic into structured notes
        topic = st.text_input(
            "Topic",
            placeholder="e.g., Neural Networks, French Revolution, Chemical Bonding",
        )
        depth = st.select_slider(
            "Depth",
            options=["Overview", "Standard", "In-depth"],
            value="Standard",
        )

        if st.button("Generate Topic Notes", type="primary"):
            if not topic.strip():
                st.warning("Please enter a topic.")
            else:
                system_prompt = (
                    "You are an expert tutor. Create structured study notes on the given topic.\n"
                    "- Use headings and bullet points.\n"
                    "- Include definitions, key formulas or dates, and simple examples.\n"
                    f"- Depth: {depth}.\n"
                    f"- Overall study mode: {study_mode}."
                )
                user_prompt = f"Create study notes on: {topic}"
                with st.spinner("Generating notes..."):
                    notes = call_study_agent(
                        system_prompt,
                        user_prompt,
                        model=model_choice,
                        temperature=creativity,
                    )
                st.markdown("### 📘 Generated Notes")
                st.write(notes)

# ---------- Tab 3: Quizzes ----------
with tab_quiz:
    st.subheader("Generate quizzes")

    quiz_topic = st.text_input(
        "Quiz topic",
        placeholder="e.g., Photosynthesis, Data Structures, World War I",
    )
    num_questions = st.slider("Number of questions", min_value=3, max_value=20, value=5)
    quiz_type = st.selectbox(
        "Quiz type",
        ["Multiple choice", "Short answer", "Mixed"],
        index=0,
    )
    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard", "Mixed"],
        index=1,
    )

    if st.button("Generate Quiz", type="primary"):
        if not quiz_topic.strip():
            st.warning("Please enter a quiz topic.")
        else:
            system_prompt = (
                "You are an AI quiz generator for students.\n"
                "Create a quiz in Markdown format. Include clear numbering.\n"
                f"- Question type: {quiz_type}.\n"
                f"- Difficulty: {difficulty}.\n"
                f"- Overall study mode: {study_mode}.\n"
                "- After the questions, provide an answer key clearly separated."
            )
            user_prompt = (
                f"Create a {num_questions}-question quiz on the topic: {quiz_topic}.\n"
                "Use friendly wording appropriate for students."
            )
            with st.spinner("Creating quiz..."):
                quiz = call_study_agent(
                    system_prompt,
                    user_prompt,
                    model=model_choice,
                    temperature=creativity,
                )
            st.markdown("### 🧠 Generated Quiz")
            st.markdown(quiz)

# ---------- Tab 4: Study Reminders ----------
with tab_reminders:
    st.subheader("Set and view study reminders")

    reminder_text = st.text_input(
        "Reminder text",
        placeholder="e.g., Revise chapter 3, practice 10 problems, review vocabulary",
    )
    reminder_date = st.date_input("Target date", datetime.date.today())
    reminder_time = st.time_input("Target time", datetime.time(hour=18, minute=0))

    if st.button("Add Reminder"):
        if not reminder_text.strip():
            st.warning("Please enter a reminder.")
        else:
            st.session_state["reminders"].append(
                {
                    "text": reminder_text.strip(),
                    "date": reminder_date.isoformat(),
                    "time": reminder_time.strftime("%H:%M"),
                }
            )
            st.success("Reminder added!")

    st.markdown("### 📅 Your Reminders")
    if not st.session_state["reminders"]:
        st.info("No reminders yet. Add one above.")
    else:
        for i, r in enumerate(st.session_state["reminders"], start=1):
            st.write(f"**{i}.** {r['text']} — `{r['date']} {r['time']}`")

        if st.button("Clear All Reminders"):
            st.session_state["reminders"] = []
            st.success("All reminders cleared.")
