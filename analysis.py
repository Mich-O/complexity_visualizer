from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12331Mysql@localhost:3306/airbnb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///analysis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

my_db = SQLAlchemy(app)

# ==================== DATABASE MODEL ====================
class AnalysisResults(my_db.Model):
    __tablename__ = "analysis_results"
    id = my_db.Column(my_db.Integer, primary_key=True)
    algorithm = my_db.Column(my_db.String(50), nullable=False)
    items = my_db.Column(my_db.Integer, nullable=False)
    steps = my_db.Column(my_db.Integer, nullable=False)
    start_time = my_db.Column(my_db.Float, nullable=False)
    end_time = my_db.Column(my_db.Float, nullable=False)
    total_time = my_db.Column(my_db.Float, nullable=False)
    time_complexity = my_db.Column(my_db.String(20), nullable=False)
    graph_image_path = my_db.Column(my_db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "algorithm": self.algorithm,
            "items": self.items,
            "steps": self.steps,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_time_ms": self.total_time,
            "time_complexity": self.time_complexity,
            "graph_image_path": self.graph_image_path
        }

# ==================== ALGORITHMS ====================
def linear_search(n):
    for i in range(n):
        if i == n-1:
            return i

def bubble_sort(n):
    arr = np.random.randint(0, 100, n)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def binary_search(n):
    arr = sorted(np.random.randint(0, 100, n))
    target = arr[-1]
    left, right = 0, n - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def nested_loops(n):
    count = 0
    for i in range(n):
        for j in range(n):
            count += 1
    return count

# ==================== ALGORITHM MAPPING ====================
ALGORITHMS = {
    'bubble': (bubble_sort, 'O(n²)'),
    'linear': (linear_search, 'O(n)'),
    'binary': (binary_search, 'O(log n)'),
    'nested': (nested_loops, 'O(n²)')
}

# ==================== TIME COMPLEXITY ANALYZER ====================
def time_complexity_visualizer(algorithm, n_min, n_max, n_step):
    times = []
    input_sizes = list(range(n_min, n_max + n_step, n_step))
    
    for n in input_sizes:
        start_time = time.time()
        algorithm(n)
        end_time = time.time()
        times.append(end_time - start_time)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(input_sizes, times, 'o-', linewidth=2, markersize=6)
    ax.set_xlabel('Input size', fontsize=12)
    ax.set_ylabel('Running time (seconds)', fontsize=12)
    ax.set_title('Algorithm Time Complexity Visualization', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Convert plot to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    
    return img_base64

# ==================== ENDPOINTS ====================

@app.route('/analyze', methods=['GET'])
def analyze():
    """
    Endpoint: /analyze?algo=bubble&n=1000&steps=10
    """
    try:
        # Get query parameters
        algo_name = request.args.get('algo', '').lower()
        n = int(request.args.get('n', 1000))
        steps = int(request.args.get('steps', 10))
        
        # Validate algorithm
        if algo_name not in ALGORITHMS:
            return jsonify({
                "error": f"Invalid algorithm. Choose from: {list(ALGORITHMS.keys())}"
            }), 400
        
        algorithm, complexity = ALGORITHMS[algo_name]
        
        # Run analysis
        start_time = time.time()
        graph_base64 = time_complexity_visualizer(algorithm, steps, n, steps)
        end_time = time.time()
        
        total_time_ms = (end_time - start_time) * 1000
        
        # Prepare response
        response = {
            "algo": algo_name,
            "items": n,
            "steps": steps,
            "start_time": start_time,
            "end_time": end_time,
            "total_time_ms": round(total_time_ms, 2),
            "time_complexity": complexity,
            "graph_image_path": f"data:image/png;base64,{graph_base64}"
        }
        
        return jsonify(response), 200
    
    except ValueError as e:
        return jsonify({"error": f"Invalid parameters: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/save_analysis', methods=['POST'])
def save_analysis():
    """
    Endpoint: POST /save_analysis
    Body: JSON with analysis results
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['algo', 'items', 'steps', 'start_time', 'end_time', 
                          'total_time_ms', 'time_complexity', 'graph_image_path']
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create new analysis record
        new_analysis = AnalysisResults(
            algorithm=data['algo'],
            items=data['items'],
            steps=data['steps'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            total_time=data['total_time_ms'],
            time_complexity=data['time_complexity'],
            graph_image_path=data['graph_image_path']
        )
        
        # Save to database
        my_db.session.add(new_analysis)
        my_db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Analysis saved successfully",
            "id": new_analysis.id
        }), 201
    
    except Exception as e:
        my_db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/retrieve_analysis', methods=['GET'])
def retrieve_analysis():
    """
    Endpoint: /retrieve_analysis?id=1
    """
    try:
        analysis_id = request.args.get('id')
        
        if not analysis_id:
            return jsonify({"error": "Missing 'id' query parameter"}), 400
        
        # Query database
        analysis = AnalysisResults.query.get(int(analysis_id))
        
        if not analysis:
            return jsonify({"error": f"No analysis found with id {analysis_id}"}), 404
        
        return jsonify(analysis.to_dict()), 200
    
    except ValueError:
        return jsonify({"error": "Invalid id format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/all_analyses', methods=['GET'])
def all_analyses():
    """
    Bonus endpoint: Get all analyses
    """
    try:
        analyses = AnalysisResults.query.all()
        return jsonify([analysis.to_dict() for analysis in analyses]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== MAIN ====================
if __name__ == '__main__':
    with app.app_context():
        print("Creating database tables...")
        my_db.create_all()
        print("✓ Database tables created!")
    
    app.run(host="0.0.0.0", port=3000, debug=True)