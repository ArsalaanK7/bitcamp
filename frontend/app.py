# frontend/app.py
import streamlit as st

st.title("NeuraCoach 🧠💪")
mood = st.slider("How are you feeling today?", 0, 10, 5)
sleep = st.slider("Hours of sleep last night", 0, 12, 7)
energy = st.slider("How much energy do you have?", 0, 10, 5)

if st.button("Generate Daily Plan"):
    st.write("🧘 10-minute meditation")
    st.write("🚶 15-minute walk")
    st.write("📝 Journal your thoughts tonight")
