🎓 Multi-Agent Personal Study Assistant

An interactive AI-powered study companion built using Python, Streamlit, Google Gemini API, and optional CrewAI support.
This assistant helps students ask questions, generate summaries, create quizzes, and set study reminders — all inside a clean, animated, user-friendly interface.

 Features
 1. Ask Questions (Q&A Agent)
Uses Google Gemini to answer any study-related question.
Supports Simple, Detailed, and Step-by-step explanations.
Adapts responses to school, college, or general levels.
Adjustable creativity and study mode (balanced, exam prep, deep understanding).

 2. Notes & Summaries Agent
Summarizes long notes or textbook content.
Creates structured notes for any topic.
Supports different summary lengths.
Can highlight key terms automatically.

3. Quiz Generator Agent
Generates MCQs, short answers, or mixed quizzes.
Difficulty levels: Easy, Medium, Hard, Mixed.
Includes an answer key at the end.

 4. Study Reminder System
Add custom reminders with date + time.
All reminders stored using Streamlit session state.
Option to clear reminders.

 5. Optional CrewAI Integration (Multi-Agent backend)
If CrewAI is installed, the app can use a team-based AI agent for Q&A.
Requires OPENAI_API_KEY or supported provider.

🛠 Tech Stack
Component	Technology
UI Framework	Streamlit
LLM Model	Google Gemini (gemini-2.0-flash / gemini-2.0-pro)
Multi-Agent Support	CrewAI (optional)
Environment Management	dotenv (.env)
Backend Logic	Python
Styling	Custom CSS animations
📁 Project Structure (based on your code)

project/
│── app.py                     # Main Streamlit application
│── .env                       # API keys (GOOGLE_API_KEY, OPENAI_API_KEY)
│── requirements.txt           # Dependencies
│── README.md                  # Project documentation

🔑 Requirements
Make sure to install:
streamlit
python-dotenv
google-generativeai
crewai   (optional)


Install using:

pip install -r requirements.txt

🔧 Environment Variables

Create a .env file:

GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_key   # Only if using CrewAI

 How to Run
streamlit run app.py

This will launch the UI in your browser.

 How It Works (Internal Logic)
✔ call_study_agent()

Sends system + user prompts to Google Gemini.
Handles temperature, output tokens, and model selection.
✔ call_crewai_study_agent()
Runs a CrewAI agent with a task and returns its output.
Used only if CrewAI + API key is available.

✔ Streamlit Tabs
Ask Questions
Notes & Summaries
Quiz Generator\
Study Reminders

✔ UI Enhancements
Custom animations for headers
Hover effects on metric cards
Stylish tabs with accent glow
