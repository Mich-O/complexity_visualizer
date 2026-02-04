from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://waka:spatni@localhost:3306/airbnb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

my_db = SQLAlchemy(app)

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
            "total_time": self.total_time,
            "time_complexity": self.time_complexity,
            "graph_image_path": self.graph_image_path
        }

if __name__ == '__main__':
    # Create all database tables
    with app.app_context():
        print("RUNNING")
        my_db.create_all()
        print("✓ Database tables created!")
    app.run(host="0.0.0.0", port=8080, debug=True)