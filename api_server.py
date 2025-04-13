from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.planningAgent import PlannerAgent

app = Flask(__name__)
CORS(app)

planner_agent = PlannerAgent()

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json()
        tasks = data.get('tasks', [])
        
        if not tasks:
            return jsonify({'error': 'No tasks provided'}), 400
            
        plan = planner_agent.generate_plan(tasks)
        return jsonify({'plan': plan})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 