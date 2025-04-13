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
            temperature=0.7,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )

    def construct_prompt(self, tasks: list) -> str:
        """
        Constructs a prompt for generating a daily plan based on user tasks.
        """
        tasks_str = ", ".join(tasks)
        prompt = (
            f"User Tasks: {tasks_str}\n\n"
            "Create a comprehensive daily schedule that MUST include ALL of the following user tasks: "
            f"{tasks_str}\n\n"
            "IMPORTANT: You must include EVERY task mentioned above. Do not skip or omit any tasks. Only provide the tasks, no other text."
            "For each task, provide specific but brief details."
            "Also include complementary activities and breaks that would enhance productivity and well-being.\n\n"
            "Format the response as a list of specific, actionable items, one per line. "
            "Each line should be a complete, standalone task or activity. "
            "Example format:\n"
            "Review class notes and create study outline\n"
            "Complete math homework problems\n"
            "Quick walk outside\n"
            "Work on programming assignment\n"
            "Prepare meals for the week\n"
            "Go for a 30-minute jog and stretching\n"
            "Cook dinner\n"
            "Requirements:\n"
            "1. EVERY user task must be included in the plan. You may initially add 3-4 complementary tasks to helpwith the user tasks, but you must not skip or omit any user tasks.\n"
            "2. Each line must be a complete, actionable item\n"
            "3. Add appropriate breaks between tasks\n"
            "4. Include no more than 3-4 complementary activities. The rest of the tasks should made up of the user's goals."
            "5. Consider energy levels throughout the day"
            "6. Make sure the plan is realistic and achievable. Large tasks may be split up into smaller tasks if that will help."
            "7. You must not include any redundant tasks."
            "8. The total number of tasks should be between 5-7. This should only change if the user asks for more than 7 tasks to be made. "
            "9. Don't generate dummy data or placeholders. If you don't have specific information, you can leave it vague. For example 'Eat dinner at [insert restaurant name]' can just be 'Eat dinner'"
            "10. You should never include times in the plan." 
        )
        return prompt

    def generate_complementary_task(self, completed_task: str, all_tasks: list) -> str:
        """
        Generates a complementary task based on the completed task and current task list.
        """
        prompt = (
            f"Completed Task: {completed_task}\n"
            f"Current Tasks: {', '.join(all_tasks)}\n\n"



            "Generate ONE complementary task that would enhance productivity or well-being. ONLY generate the task, no other text. "
            "The task should:\n"
            "1. Be directly related to the completed task or overall goals it is preferred that it is related to the recently completed task\n"
            "2. Be a standalone, actionable item\n"
            "3. Be different from existing tasks\n"
            "4. Be realistic and achievable\n"
            "5. Be brief and to the point. One sentence should suffice. \n"
            "6. You should never include times in the plan."
        )
        
        messages = [
            (
                "system",
                "You are a helpful assistant that suggests complementary tasks. "
                "Provide ONE specific, actionable task that complements the completed task. "
                "Make it realistic and achievable."
            ),
            ("human", prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return self.parse_response(response)
        except Exception as e:
            print(f"Error generating complementary task: {e}")
            return ""

    def validate_plan(self, plan: str, tasks: list) -> bool:
        """
        Validates that all user tasks are included in the generated plan.
        """
        plan_lower = plan.lower()
        for task in tasks:
            task_lower = task.lower()
            if task_lower not in plan_lower:
                return False
        return True

    def generate_plan(self, tasks: list) -> str:
        """
        Generates a personalized daily plan using the Gemini model.
        """
        prompt = self.construct_prompt(tasks)
        messages = [
            (
                "system",
                "You are a helpful assistant specialized in creating efficient daily schedules. "
                "You MUST include ALL tasks provided by the user, with specific details. "
                "Format your response as a list of specific, actionable items, one per line. "
                "Each line should be a complete, standalone task or activity.. "
                "Do not skip or omit any tasks. Also suggest complementary activities and breaks that would enhance productivity and well-being."
            ),
            ("human", prompt)
        ]
        try:
            response = self.llm.invoke(messages)
            plan = self.parse_response(response)
            
            # Validate that all tasks are included
            if not self.validate_plan(plan, tasks):
                # If validation fails, try generating the plan again
                response = self.llm.invoke(messages)
                plan = self.parse_response(response)
                
            return plan
        except Exception as e:
            print(f"Error generating plan: {e}")
            return (
                "8:00 AM - 9:00 AM: Start with your most important tasks\n"
                "9:00 AM - 9:15 AM: Take a short break\n"
                "9:15 AM - 10:30 AM: Continue with remaining tasks\n"
                "10:30 AM - 10:45 AM: Quick stretch break\n"
                "10:45 AM - 12:00 PM: Focus on priority tasks\n"
                "12:00 PM - 1:00 PM: Lunch break\n"
                "1:00 PM - 2:30 PM: Afternoon work session\n"
                "2:30 PM - 2:45 PM: Short walk break\n"
                "2:45 PM - 4:00 PM: Complete remaining tasks\n"
                "4:00 PM - 5:00 PM: Wind down activities\n"
                "5:00 PM - 6:00 PM: Dinner preparation\n"
                "6:00 PM - 7:00 PM: Relax and unwind"
            )

    def parse_response(self, response) -> str:
        """
        Extracts and cleans the human-readable content from the response.
        """
        if isinstance(response, dict) and "content" in response:
            return response["content"].strip()
        elif hasattr(response, "content"):
            return response.content.strip()
        return str(response).strip()

# Example usage:
if __name__ == "__main__":
    # Sample test data
    tasks = ["homework", "exercise", "meal prepping"]
    
    planner = PlannerAgent()
    daily_plan = planner.generate_plan(tasks)
    print("Today's Personalized Plan:\n")
    print(daily_plan)
