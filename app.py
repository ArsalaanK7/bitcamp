import streamlit as st
import numpy as np
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
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
        'current_plan': None,
        'completed_activities': {},  # Dictionary to track completed activities
        'daily_goal': ""  # Store the user's daily goal
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
        
        # Initialize completed activities for the new plan
        st.session_state.user_state['completed_activities'] = {
            rec: False for rec in recommendations
        }
        
        # Show feedback
        st.success(feedback['mood_feedback'])
        st.info(feedback['energy_feedback'])
        if feedback['sleep_advice']:
            st.warning(feedback['sleep_advice'])

# Main content area
# Daily goal input
st.header("What do you want to get done today?")
daily_goal = st.text_input("Enter your goal for today", value=st.session_state.user_state['daily_goal'])

# Update the daily goal in session state
if daily_goal != st.session_state.user_state['daily_goal']:
    st.session_state.user_state['daily_goal'] = daily_goal
    
    # If we have a goal and no plan yet, generate a new plan
    if daily_goal and not st.session_state.user_state['current_plan']:
        # Get personalized recommendations based on the goal
        recommendations = recommendation_agent.get_recommendations(
            mood=mood,
            sleep_hours=sleep_hours,
            energy_level=energy_level,
            goal=daily_goal  # Pass the goal to the recommendation agent
        )
        
        st.session_state.user_state['current_plan'] = recommendations
        
        # Initialize completed activities for the new plan
        st.session_state.user_state['completed_activities'] = {
            rec: False for rec in recommendations
        }
        
        st.success("I've created a personalized plan based on your goal!")

# Display the personalized plan
if st.session_state.user_state['current_plan']:
    st.header("Your Personalized Plan")
    
    # Show the user's goal if available
    if st.session_state.user_state['daily_goal']:
        st.subheader(f"Goal: {st.session_state.user_state['daily_goal']}")
    
    # Create a checklist for the plan items
    for rec in st.session_state.user_state['current_plan']:
        # Check if this activity is already completed
        is_completed = st.session_state.user_state['completed_activities'].get(rec, False)
        
        # Create a checkbox for each recommendation
        if st.checkbox(rec, value=is_completed, key=f"check_{rec}"):
            # If the activity is checked and wasn't completed before
            if not is_completed:
                # Update the completed status
                st.session_state.user_state['completed_activities'][rec] = True
                
                # Log the activity with current mood and energy
                st.session_state.user_state['activity_history'].append({
                    'timestamp': datetime.now(),
                    'activity': rec,
                    'mood': mood,
                    'energy': energy_level
                })
                
                # Update RL engine
                rl_engine.update(rec, mood)
                
                # Show success message
                st.success(f"Great job completing: {rec}!")
    
    # Activity log section
    st.header("Activity Log")
    if st.session_state.user_state['activity_history']:
        # Create a DataFrame for the activity log
        activity_log = pd.DataFrame(st.session_state.user_state['activity_history'])
        
        # Format the timestamp for display
        activity_log['formatted_time'] = activity_log['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Display the activity log
        st.dataframe(
            activity_log[['formatted_time', 'activity', 'mood', 'energy']].rename(
                columns={
                    'formatted_time': 'Time',
                    'activity': 'Activity',
                    'mood': 'Mood',
                    'energy': 'Energy'
                }
            ),
            hide_index=True
        )
    else:
        st.info("Complete activities from your plan to see them logged here.")

# Progress visualization
if st.session_state.user_state['mood_history']:
    st.header("Your Progress")
    
    # Create DataFrame from history
    history_data = pd.DataFrame(st.session_state.user_state['mood_history'])
    
    # Create a multi-line chart for mood and energy
    st.subheader("Mood & Energy Trends")
    
    # Set dark mode style for matplotlib
    plt.style.use('dark_background')
    
    # Create a matplotlib figure for more control over the chart
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0E1117')  # Match Streamlit's dark background
    ax.set_facecolor('#0E1117')  # Match Streamlit's dark background
    
    # Plot the data with bright colors for visibility
    ax.plot(history_data['timestamp'], history_data['mood'], label='Mood', marker='o', color='#00FF00', linewidth=2)
    ax.plot(history_data['timestamp'], history_data['energy'], label='Energy Level', marker='s', color='#00FFFF', linewidth=2)
    
    # Set axis labels with white text
    ax.set_xlabel('Time', color='white')
    ax.set_ylabel('Level', color='white')
    
    # Set y-axis limits
    ax.set_ylim(0, 10)
    
    # Format x-axis to show full timestamps
    fig.autofmt_xdate()  # Rotate and align the tick labels
    
    # Set tick colors to white
    ax.tick_params(colors='white')
    
    # Add legend with white text
    ax.legend(facecolor='#0E1117', edgecolor='white', labelcolor='white')
    
    # Add grid with subtle lines
    ax.grid(True, linestyle='--', alpha=0.3, color='white')
    
    # Set spines color to white
    for spine in ax.spines.values():
        spine.set_color('white')
    
    # Display the chart
    st.pyplot(fig)
    
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