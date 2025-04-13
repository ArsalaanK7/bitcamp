import streamlit as st
import numpy as np
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from agents.planningAgent import PlannerAgent
from agents.reflection_agent import ReflectionAgent
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
        'daily_goal': "",  # Store the user's daily goal
        'suggested_task': None,  # Store the current suggested task
        'last_completed_task': None,  # Store the last completed task
        'task_added': False,  # Flag to track if a task was just added
        'task_declined': False,  # Flag to track if a task was just declined
        'editing_activity': None,  # Store the activity being edited
        'show_mood_input': False,  # Flag to show mood input popup
        'checkin_completed': False  # Flag to track if daily check-in is completed
    }

# Initialize agents
planner_agent = PlannerAgent()
reflection_agent = ReflectionAgent()
checkin_agent = CheckinAgent()
rl_engine = RLEngine()

# App title and description
st.title("NeuraCoach")
st.markdown("Your adaptive AI wellness partner for mind and body")

# Daily check-in modal
if not st.session_state.user_state['checkin_completed']:
    with st.form("daily_checkin"):
        st.header("Daily Check-in")
        mood = st.slider("How are you feeling today?", 1, 10, 5)
        sleep_hours = st.number_input("Hours of sleep last night", 0.0, 12.0, 7.0)
        energy_level = st.slider("Energy level", 1, 10, 5)
        
        submitted = st.form_submit_button("Submit Check-in")
        
        if submitted:
            # Update user state
            st.session_state.user_state['mood_history'].append({
                'timestamp': datetime.now(),
                'mood': mood,
                'sleep': sleep_hours,
                'energy': energy_level
            })
            
            # Get check-in feedback
            feedback = checkin_agent.get_checkin_feedback(mood, energy_level, sleep_hours)
            
            # Get personalized recommendations using planning agent
            recommendations = planner_agent.generate_plan([
                f"Adjust mood to {mood}/10",
                f"Maintain energy at {energy_level}/10",
                f"Ensure {sleep_hours} hours of sleep"
            ])
            
            st.session_state.user_state['current_plan'] = recommendations
            
            # Initialize completed activities for the new plan
            st.session_state.user_state['completed_activities'] = {
                rec: False for rec in recommendations.split('\n') if rec.strip()
            }
            
            # Mark check-in as completed
            st.session_state.user_state['checkin_completed'] = True
            
            # Show feedback
            st.success(feedback['mood_feedback'])
            st.info(feedback['energy_feedback'])
            if feedback['sleep_advice']:
                st.warning(feedback['sleep_advice'])
            
            st.rerun()

# Main content area
if st.session_state.user_state['checkin_completed']:
    # Daily goal input
    st.header("What do you want to get done today?")
    daily_goal = st.text_input("Enter your goal for today", value=st.session_state.user_state['daily_goal'])
    
    # Update the daily goal in session state
    if daily_goal != st.session_state.user_state['daily_goal']:
        st.session_state.user_state['daily_goal'] = daily_goal
        
        # If we have a goal, generate a new plan
        if daily_goal:
            # Get personalized recommendations based on the goal
            recommendations = planner_agent.generate_plan([daily_goal])
            
            st.session_state.user_state['current_plan'] = recommendations
            
            # Initialize completed activities for the new plan
            st.session_state.user_state['completed_activities'] = {
                rec: False for rec in recommendations.split('\n') if rec.strip()
            }
            
            # Clear any existing suggested task
            st.session_state.user_state['suggested_task'] = None
            st.session_state.user_state['task_added'] = False
            st.session_state.user_state['task_declined'] = False
            
            st.success("I've created a new personalized plan based on your updated goal!")
            st.rerun()
    
    # Display the personalized plan
    if st.session_state.user_state['current_plan']:
        st.header("Your Personalized Plan")
        
        # Show the user's goal if available
        if st.session_state.user_state['daily_goal']:
            st.subheader(f"Goal: {st.session_state.user_state['daily_goal']}")
        
        # Add manual task input
        with st.expander("➕ Add Task", expanded=False):
            col1, col2 = st.columns([4, 1])
            with col1:
                new_task = st.text_input("", placeholder="Enter task", key="new_task_input", label_visibility="collapsed")
            with col2:
                if st.button("Add", use_container_width=True):
                    if new_task.strip():
                        # Add the new task to the plan
                        new_plan = st.session_state.user_state['current_plan'] + "\n" + new_task
                        st.session_state.user_state['current_plan'] = new_plan
                        st.session_state.user_state['completed_activities'][new_task] = False
                        st.success("Task added to your plan!")
                        st.rerun()
        
        # Create a checklist for the plan items
        plan_items = st.session_state.user_state['current_plan'].split('\n')
        for rec in plan_items:
            if rec.strip():  # Only process non-empty lines
                # Check if this activity is already completed
                is_completed = st.session_state.user_state['completed_activities'].get(rec, False)
                
                # Create a checkbox for each recommendation
                if st.checkbox(rec, value=is_completed, key=f"check_{rec}"):
                    # If the activity is checked and wasn't completed before
                    if not is_completed:
                        # Update the completed status
                        st.session_state.user_state['completed_activities'][rec] = True
                        
                        # Store the completed task
                        st.session_state.user_state['last_completed_task'] = rec
                        
                        # Set flag to show mood input
                        st.session_state.user_state['show_mood_input'] = True
                        
                        # Generate a complementary task
                        current_tasks = [task for task in plan_items if task.strip()]
                        suggested_task = planner_agent.generate_complementary_task(rec, current_tasks)
                        if suggested_task:
                            st.session_state.user_state['suggested_task'] = suggested_task
                        
                        # Show success message
                        st.success(f"Great job completing: {rec}!")
                
                # Show mood input popup if this is the last completed task
                if (st.session_state.user_state['show_mood_input'] and 
                    rec == st.session_state.user_state['last_completed_task']):
                    with st.expander("Rate your feelings", expanded=True):
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col1:
                            st.markdown("**Mood**")
                            post_mood = st.slider("", 1, 10, 5, key=f"post_mood_{rec}", label_visibility="collapsed")
                        with col2:
                            st.markdown("**Energy**")
                            post_energy = st.slider("", 1, 10, 5, key=f"post_energy_{rec}", label_visibility="collapsed")
                        with col3:
                            st.markdown("&nbsp;")  # Empty space for alignment
                            if st.button("Save", key=f"save_mood_{rec}", use_container_width=True):
                                # Log the activity with post-task mood and energy
                                st.session_state.user_state['activity_history'].append({
                                    'timestamp': datetime.now(),
                                    'activity': rec,
                                    'mood': post_mood,
                                    'energy': post_energy
                                })
                                
                                # Add the post-task mood and energy to the mood history
                                st.session_state.user_state['mood_history'].append({
                                    'timestamp': datetime.now(),
                                    'mood': post_mood,
                                    'sleep': None,  # No sleep data for post-task check-ins
                                    'energy': post_energy
                                })
                                
                                # Update RL engine
                                rl_engine.update(rec, post_mood)
                                
                                # Remove the completed task from the plan
                                current_plan = st.session_state.user_state['current_plan'].split('\n')
                                current_plan = [task for task in current_plan if task.strip() != rec]
                                st.session_state.user_state['current_plan'] = '\n'.join(current_plan)
                                
                                # Reset flags
                                st.session_state.user_state['show_mood_input'] = False
                                st.session_state.user_state['last_completed_task'] = None
                                st.rerun()
        
        # Show suggested task if available
        if st.session_state.user_state['suggested_task'] and not st.session_state.user_state['task_added'] and not st.session_state.user_state['task_declined']:
            st.subheader("Suggested Next Task")
            st.write(st.session_state.user_state['suggested_task'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add to Plan"):
                    # Add the suggested task to the plan
                    new_plan = st.session_state.user_state['current_plan'] + "\n" + st.session_state.user_state['suggested_task']
                    st.session_state.user_state['current_plan'] = new_plan
                    st.session_state.user_state['completed_activities'][st.session_state.user_state['suggested_task']] = False
                    st.session_state.user_state['suggested_task'] = None
                    st.session_state.user_state['task_added'] = True
                    st.success("Task added to your plan!")
                    st.rerun()
            with col2:
                if st.button("Decline"):
                    st.session_state.user_state['suggested_task'] = None
                    st.session_state.user_state['task_declined'] = True
                    st.info("Task declined.")
                    st.rerun()
        
        # Reset the flags after the state has been updated
        if st.session_state.user_state['task_added'] or st.session_state.user_state['task_declined']:
            st.session_state.user_state['task_added'] = False
            st.session_state.user_state['task_declined'] = False
        
        # Activity log section
        st.header("Activity Log")
        st.write("Double click any box to edit its contents.")
        if st.session_state.user_state['activity_history']:
            # Create a DataFrame for the activity log
            activity_log = pd.DataFrame(st.session_state.user_state['activity_history'])
            
            # Format the timestamp for display
            activity_log['formatted_time'] = activity_log['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            
            # Create editable table
            edited_df = st.data_editor(
                activity_log[['formatted_time', 'activity', 'mood', 'energy']].rename(
                    columns={
                        'formatted_time': 'Time',
                        'activity': 'Activity',
                        'mood': 'Mood',
                        'energy': 'Energy'
                    }
                ),
                column_config={
                    "Mood": st.column_config.NumberColumn(
                        "Mood",
                        min_value=1,
                        max_value=10,
                        step=1,
                        format="%d"
                    ),
                    "Energy": st.column_config.NumberColumn(
                        "Energy",
                        min_value=1,
                        max_value=10,
                        step=1,
                        format="%d"
                    )
                },
                hide_index=True,
                key="activity_editor"
            )
            
            # Update the activity history if changes were made
            if not edited_df.equals(activity_log[['formatted_time', 'activity', 'mood', 'energy']].rename(
                columns={
                    'formatted_time': 'Time',
                    'activity': 'Activity',
                    'mood': 'Mood',
                    'energy': 'Energy'
                }
            )):
                # Convert the edited DataFrame back to the original format
                updated_history = []
                for _, row in edited_df.iterrows():
                    # Find the original timestamp for this activity
                    original_entry = next(
                        (entry for entry in st.session_state.user_state['activity_history']
                         if entry['activity'] == row['Activity']),
                        None
                    )
                    if original_entry:
                        updated_history.append({
                            'timestamp': original_entry['timestamp'],
                            'activity': row['Activity'],
                            'mood': int(row['Mood']),
                            'energy': int(row['Energy'])
                        })
                
                st.session_state.user_state['activity_history'] = updated_history
                st.rerun()
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