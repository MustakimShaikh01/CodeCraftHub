# CodeCraftHub - Simple Learning Platform API
# Flask REST API for managing developer learning courses
# Data is stored in a JSON file (no database required)

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = "courses.json"


# -----------------------------
# Helper Functions
# -----------------------------

def load_courses():
    """Load courses from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_courses(courses):
    """Save courses to JSON file"""
    with open(DATA_FILE, "w") as f:
        json.dump(courses, f, indent=2)


def get_next_id(courses):
    """Generate next ID"""
    if not courses:
        return 1
    return max(c["id"] for c in courses) + 1


# -----------------------------
# Root Route
# -----------------------------

@app.route("/")
def home():
    return jsonify({
        "message": "CodeCraftHub API is running",
        "endpoints": [
            "/api/courses",
            "/api/courses/<id>",
            "/api/courses/stats"
        ]
    })


# -----------------------------
# GET all courses
# -----------------------------

@app.route("/api/courses", methods=["GET"])
def get_courses():
    courses = load_courses()
    return jsonify({
        "success": True,
        "count": len(courses),
        "courses": courses
    })


# -----------------------------
# GET single course
# -----------------------------

@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    courses = load_courses()

    for c in courses:
        if c["id"] == course_id:
            return jsonify({
                "success": True,
                "course": c
            })

    return jsonify({
        "success": False,
        "error": "Course not found"
    }), 404


# -----------------------------
# CREATE course
# -----------------------------

@app.route("/api/courses", methods=["POST"])
def create_course():

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    required = ["name", "description", "target_date", "status"]

    for field in required:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing field: {field}"
            }), 400

    courses = load_courses()

    new_course = {
        "id": get_next_id(courses),
        "name": data["name"],
        "description": data["description"],
        "target_date": data["target_date"],
        "status": data["status"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    courses.append(new_course)
    save_courses(courses)

    return jsonify({
        "success": True,
        "course": new_course
    }), 201


# -----------------------------
# UPDATE course
# -----------------------------

@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):

    courses = load_courses()
    data = request.get_json()

    for course in courses:

        if course["id"] == course_id:

            course["name"] = data.get("name", course["name"])
            course["description"] = data.get("description", course["description"])
            course["target_date"] = data.get("target_date", course["target_date"])
            course["status"] = data.get("status", course["status"])

            save_courses(courses)

            return jsonify({
                "success": True,
                "course": course
            })

    return jsonify({
        "success": False,
        "error": "Course not found"
    }), 404


# -----------------------------
# DELETE course
# -----------------------------

@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):

    courses = load_courses()

    updated_courses = [c for c in courses if c["id"] != course_id]

    if len(updated_courses) == len(courses):
        return jsonify({
            "success": False,
            "error": "Course not found"
        }), 404

    save_courses(updated_courses)

    return jsonify({
        "success": True,
        "message": "Course deleted"
    })


# -----------------------------
# COURSE STATS
# -----------------------------

@app.route("/api/courses/stats", methods=["GET"])
def stats():

    courses = load_courses()

    stats = {
        "total": len(courses),
        "Not Started": 0,
        "In Progress": 0,
        "Completed": 0
    }

    for c in courses:
        if c["status"] in stats:
            stats[c["status"]] += 1

    return jsonify(stats)


# -----------------------------
# Run Server
# -----------------------------

if __name__ == "__main__":
    print("CodeCraftHub API running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)