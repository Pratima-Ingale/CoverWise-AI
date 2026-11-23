#!/usr/bin/env python
"""
CoverWise AI - Property & Casualty Insurance Recommendation Agent
Entry point for starting the Flask development server.
"""
from src import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 65)
    print(" 🚀 CoverWise AI – Property & Casualty Insurance Agent")
    print("=" * 65)
    print(" Web Server running at: http://127.0.0.1:5000/")
    print(" Pages available:")
    print("   • Home:             http://127.0.0.1:5000/")
    print("   • User Input:       http://127.0.0.1:5000/input")
    print("   • Recommendations:  http://127.0.0.1:5000/recommendations")
    print("   • Policy Compare:   http://127.0.0.1:5000/compare")
    print("=" * 65)
    app.run(host='127.0.0.1', port=5000, debug=True)
