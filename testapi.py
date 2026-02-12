#!/usr/bin/env python3
"""
Test script for the Analysis API
"""

import requests
import json

BASE_URL = "http://localhost:3000"

print("="*60)
print("TESTING analysis.py API RESPONSES")
print("="*60)

# TEST 1: ANALYZE ENDPOINT 
print("\n1. Testing /analyze endpoint...")
print("-" * 60)

response = requests.get(f"{BASE_URL}/analyze", params={
    "algo": "bubble",
    "n": 100,
    "steps": 10
})

if response.status_code == 200:
    data = response.json()
    print(f"✓ Algorithm: {data['algo']}")
    print(f"✓ Items: {data['items']}")
    print(f"✓ Steps: {data['steps']}")
    print(f"✓ Total Time: {data['total_time_ms']} ms")
    print(f"✓ Time Complexity: {data['time_complexity']}")
    print(f"✓ Graph: {data['graph_image_path'][:50]}...")
    
    # Save for next test
    analysis_data = data
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)
    exit(1)

# TEST 2: SAVE_ANALYSIS ENDPOINT 
print("\n2. Testing /save_analysis endpoint...")
print("-" * 60)

response = requests.post(f"{BASE_URL}/save_analysis", 
                        json=analysis_data,
                        headers={"Content-Type": "application/json"})

if response.status_code == 201:
    result = response.json()
    print(f"✓ Status: {result['status']}")
    print(f"✓ Message: {result['message']}")
    print(f"✓ Saved ID: {result['id']}")
    
    saved_id = result['id']
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)
    exit(1)

# TEST 3: RETRIEVE_ANALYSIS ENDPOINT 
print("\n3. Testing /retrieve_analysis endpoint...")
print("-" * 60)

response = requests.get(f"{BASE_URL}/retrieve_analysis", params={
    "id": saved_id
})

if response.status_code == 200:
    data = response.json()
    print(f"✓ Retrieved ID: {data['id']}")
    print(f"✓ Algorithm: {data['algorithm']}")
    print(f"✓ Items: {data['items']}")
    print(f"✓ Total Time: {data['total_time_ms']} ms")
    print(f"✓ Time Complexity: {data['time_complexity']}")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)



# CURL COMMAND EXAMPLES 
print("\n\nCURL COMMAND EXAMPLES:")
print("="*60)

print("\n# 1. Analyze bubble sort:")
print(f'curl "http://localhost:3000/analyze?algo=bubble&n=1000&steps=10"')

print("\n# 2. Save analysis:")
print('''curl -X POST http://localhost:3000/save_analysis \\
  -H "Content-Type: application/json" \\
  -d '{
    "algo": "bubble",
    "items": 1000,
    "steps": 10,
    "start_time": 1234567890.123,
    "end_time": 1234567893.456,
    "total_time_ms": 3333.0,
    "time_complexity": "O(n²)",
    "graph_image_path": "data:image/png;base64,iVBORw0KG..."
  }'
''')

print("\n# 3. Retrieve analysis by ID:")
print('curl "http://localhost:3000/retrieve_analysis?id=1"')


print("\n# Test different algorithms:")
print('curl "http://localhost:3000/analyze?algo=linear&n=5000&steps=100"')
print('curl "http://localhost:3000/analyze?algo=binary&n=10000&steps=200"')
print('curl "http://localhost:3000/analyze?algo=nested&n=500&steps=50"')