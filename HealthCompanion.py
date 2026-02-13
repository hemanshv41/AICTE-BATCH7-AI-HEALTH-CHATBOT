import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import warnings

# Suppress ScriptRunContext warning
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")


# -------------------- CONFIG --------------------
# Load environment variables from .env file
load_dotenv()

# Fetch the key by the name defined in your .env file
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("API Key not found! Please check your .env file.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Note: As of 2026, ensure you are using a supported model name
# gemini-1.5-flash is currently the stable high-speed choice
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(
    page_title="AI Health Companion Pro",
    page_icon="💪",
    layout="wide"
)

# -------------------- CUSTOM STYLING --------------------

st.markdown("""
<style>
.big-title {
    font-size:40px;
    font-weight:700;
    background: linear-gradient(90deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.card {
    padding:20px;
    border-radius:15px;
    background-color:#1f2937;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">💪 AI Health Companion Pro</div>', unsafe_allow_html=True)
st.caption("Your intelligent nutrition & fitness advisor powered by Gemini")

# -------------------- SESSION STATE --------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "profile" not in st.session_state:
    st.session_state.profile = {
        "age": 25,
        "weight": 70,
        "height": 170,
        "goal": "Fat loss",
        "activity": "Moderate"
    }

# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.header("⚙️ Health Profile")

    age = st.number_input("Age", 10, 100, st.session_state.profile["age"])
    weight = st.number_input("Weight (kg)", 30, 250, st.session_state.profile["weight"])
    height = st.number_input("Height (cm)", 100, 250, st.session_state.profile["height"])

    goal = st.selectbox("Goal", ["Fat loss", "Muscle gain", "Maintenance"], index=0)
    activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"], index=1)

    if st.button("Update Profile"):
        st.session_state.profile.update({
            "age": age,
            "weight": weight,
            "height": height,
            "goal": goal,
            "activity": activity
        })
        st.success("Profile Updated!")

    # BMI Calculation
    bmi = weight / ((height/100)**2)
    st.metric("Your BMI", round(bmi, 1))

# -------------------- TABS --------------------

tab1, tab2, tab3 = st.tabs(["🥗 Meal Planner", "📸 Food Scanner", "🧠 AI Coach"])

# -------------------- MEAL PLANNER --------------------

with tab1:
    st.subheader("Generate Smart Meal Plan")

    if st.button("Create 7-Day Plan 🚀"):
        with st.spinner("Designing your optimized meal plan..."):
            prompt = f"""
            Create a high-quality 7-day meal plan.
            User Profile: {st.session_state.profile}

            Please provide:
            - Daily calorie targets
            - Macronutrient breakdown (P/C/F)
            - Specific meals for Breakfast, Lunch, Dinner, and Snacks
            - A consolidated grocery list
            - Quick prep tips for the week
            """
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error generating plan: {e}")

# -------------------- FOOD SCANNER --------------------

with tab2:
    st.subheader("AI Food Scanner")

    uploaded = st.file_uploader("Upload Food Image", type=["jpg", "png", "jpeg"])

    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Analyze 🍽️"):
            with st.spinner("Analyzing nutrition..."):
                try:
                    # Vision models require the image data
                    response = model.generate_content([
                        "Analyze this food image. Provide estimated calories, macros, a health rating (1-10), and portion advice.",
                        image
                    ])
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error analyzing image: {e}")

# -------------------- AI COACH CHAT --------------------

with tab3:
    st.subheader("Chat with Your AI Health Coach")

    # Display chat history
    for role, msg in st.session_state.chat_history:
        with st.chat_message("user" if role == "You" else "assistant"):
            st.markdown(msg)

    user_input = st.chat_input("Ask anything about diet, fitness, supplements...")

    if user_input:
        # User message
        st.session_state.chat_history.append(("You", user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        # AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                profile_context = f"User Profile: {st.session_state.profile}. "
                full_prompt = f"{profile_context}\nUser Question: {user_input}"
                
                try:
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                    st.session_state.chat_history.append(("Coach", response.text))
                except Exception as e:
                    st.error(f"Error: {e}")
