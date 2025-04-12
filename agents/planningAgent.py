import os
import getpass
import json

# Ensure the Google API key is in the environment variables.
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyADcZqw7c0SJngjdOtLyMl88Q8PCH5AJk0"

from langchain_google_genai import ChatGoogleGenerativeAI

class PlannerAgent:
    def __init__(self):
        # Initialize the Gemini model using the ChatGoogleGenerativeAI class.
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )

    def construct_prompt(self, user_profile: dict, mood_history: dict, goals: dict) -> str:
        """
        Constructs a detailed prompt containing the user's profile, mood history, and goals.
        """
        profile_str = json.dumps(user_profile)
        mood_str = json.dumps(mood_history)
        goals_str = json.dumps(goals)
        prompt = (
            f"User Profile: {profile_str}\n"
            f"Mood History: {mood_str}\n"
            f"Goals: {goals_str}\n\n"
            "Based on the above, generate a comprehensive, personalized daily wellness plan. "
            "Include detailed actionable recommendations for morning, midday, and evening routines. "
            "The plan should be supportive, motivational, and easy to follow."
        )
        return prompt

    def generate_plan(self, user_profile: dict, mood_history: dict, goals: dict) -> str:
        """
        Generates a personalized wellness plan using the Gemini model.
        This method creates a messages list with both a system message and a human message containing the prompt.
        """
        prompt = self.construct_prompt(user_profile, mood_history, goals)
        messages = [
            (
                "system",
                "You are a helpful assistant specialized in generating personalized daily wellness plans. "
                "Provide actionable and motivational recommendations for morning, midday, and evening routines."
            ),
            ("human", prompt)
        ]
        try:
            # Invoke the Gemini model with the messages list.
            response = self.llm.invoke(messages)
        except Exception as e:
            print(f"Error generating plan: {e}")
            return (
                "Default Plan: Begin your day with gentle stretching and a healthy breakfast. "
                "Midday, try to engage in a 10-minute walk or simple exercise. "
                "In the evening, wind down with mindfulness or journaling."
            )

        plan = self.parse_response(response)
        return plan

    def parse_response(self, response) -> str:
        """
        Extracts and cleans the human-readable content from the response.
        If the response includes a 'content' attribute or key, it is returned;
        otherwise, the response is converted to a string.
        """
        # Check if the response is a dictionary and has a "content" key.
        if isinstance(response, dict) and "content" in response:
            return response["content"].strip()
        # Check if the response object has a "content" attribute.
        elif hasattr(response, "content"):
            return response.content.strip()
        # Fallback: convert the response to a string.
        return str(response).strip()

# Example usage:
if __name__ == "__main__":
    # Sample test data
    user_profile = {
        "name": "Alice",
        "age": 28,
        "preferences": {"activity": "moderate", "diet": "balanced"}
    }
    mood_history = {
        "morning": "energetic",
        "afternoon": "a bit stressed",
        "evening": "calm"
    }
    goals = {
        "exercise": "include cardio and strength training",
        "relaxation": "increase mindfulness and improve sleep quality"
    }

    planner = PlannerAgent()
    daily_plan = planner.generate_plan(user_profile, mood_history, goals)
    print("Today's Personalized Wellness Plan:\n")
    print(daily_plan)
