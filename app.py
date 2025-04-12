import streamlit as st
import numpy as np
from datetime import datetime
import pandas as pd
from agents.planner_agent import PlannerAgent
from agents.reflection_agent import ReflectionAgent
from agents.recommendation_agent import RecommendationAgent
from agents.checkin_agent import CheckinAgent
from models.rl_engine import RLEngine

# Initialize session state
if 'user_state' not in st.session_state:
    st.session_state.user_state = {
        'mood_history': [],
        'activity_history': [],
        'sleep_history': [],
        'goals': [],
        'current_plan': None
    }

# Initialize agents
planner_agent = PlannerAgent()
reflection_agent = ReflectionAgent()
recommendation_agent = RecommendationAgent()
checkin_agent = CheckinAgent()
rl_engine = RLEngine()

# App title and description
st.title("NeuraCoach")
st.markdown("Your adaptive AI wellness partner for mind and body")

# Sidebar for user input
with st.sidebar:
    st.header("Daily Check-in")
    mood = st.slider("How are you feeling today?", 1, 10, 5)
    sleep_hours = st.number_input("Hours of sleep last night", 0.0, 12.0, 7.0)
    energy_level = st.slider("Energy level", 1, 10, 5)
    
    if st.button("Submit Check-in"):
        # Update user state
        st.session_state.user_state['mood_history'].append({
            'timestamp': datetime.now(),
            'mood': mood,
            'sleep': sleep_hours,
            'energy': energy_level
        })
        
        # Get check-in feedback
        feedback = checkin_agent.get_checkin_feedback(mood, energy_level, sleep_hours)
        
        # Get personalized recommendations
        recommendations = recommendation_agent.get_recommendations(
            mood=mood,
            sleep_hours=sleep_hours,
            energy_level=energy_level
        )
        
        st.session_state.user_state['current_plan'] = recommendations
        
        # Show feedback
        st.success(feedback['mood_feedback'])
        st.info(feedback['energy_feedback'])
        if feedback['sleep_advice']:
            st.warning(feedback['sleep_advice'])

# Main content area
if st.session_state.user_state['current_plan']:
    st.header("Your Personalized Plan")
    for rec in st.session_state.user_state['current_plan']:
        st.write(f"• {rec}")
    
    # Activity tracking
    st.header("Track Your Activities")
    activity = st.text_input("What activity did you complete?")
    if st.button("Log Activity"):
        st.session_state.user_state['activity_history'].append({
            'timestamp': datetime.now(),
            'activity': activity
        })
        st.success("Activity logged successfully!")
        
        # Update RL engine
        rl_engine.update(activity, mood)

# Progress visualization
if st.session_state.user_state['mood_history']:
    st.header("Your Progress")
    
    # Mood trend
    mood_data = pd.DataFrame(st.session_state.user_state['mood_history'])
    st.subheader("Mood Trend")
    st.line_chart(mood_data.set_index('timestamp')['mood'])
    
    # Get insights from reflection agent
    insights = reflection_agent.get_insights(
        st.session_state.user_state['mood_history'],
        st.session_state.user_state['activity_history'],
        st.session_state.user_state['sleep_history']
    )
    
    if insights:
        st.subheader("Insights")
        for insight in insights:
            st.write(f"💡 {insight}") 