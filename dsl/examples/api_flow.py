#!/usr/bin/env python3
"""
API integration flow example for Taskinity.
"""
import sys
import os
import json
import sqlite3

# Check if running in mock mode
if '--mock' in sys.argv:
    # Create mock task decorator
    def task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    # Create mock requests module
    class MockRequests:
        @staticmethod
        def get(url, headers=None, params=None):
            class MockResponse:
                def __init__(self, data, status_code):
                    self.data = data
                    self.status_code = status_code
                
                def json(self):
                    return self.data
                
                @property
                def text(self):
                    return json.dumps(self.data)
                
                @property
                def content(self):
                    return json.dumps(self.data).encode('utf-8')
            
            # Return mock data based on the URL
            if 'users' in url:
                return MockResponse({
                    "data": [
                        {"id": 1, "name": "John Doe", "email": "john@example.com"},
                        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
                    ],
                    "total": 3,
                    "page": 1,
                    "per_page": 10
                }, 200)
            elif 'posts' in url:
                return MockResponse({
                    "data": [
                        {"id": 1, "user_id": 1, "title": "First Post", "body": "This is the first post content"},
                        {"id": 2, "user_id": 1, "title": "Second Post", "body": "This is the second post content"},
                        {"id": 3, "user_id": 2, "title": "Another Post", "body": "This is another post content"}
                    ],
                    "total": 3,
                    "page": 1,
                    "per_page": 10
                }, 200)
            else:
                return MockResponse({"error": "Not found"}, 404)
    
    # Replace requests with mock
    requests = MockRequests()
    
    # Create mock run_flow_from_dsl function
    def run_flow_from_dsl(flow_dsl, input_data):
        print(f"Running mock API flow with input: {input_data}")
        
        # Create a mock database for testing
        db_path = input_data.get("db_path", "examples/api_data.db")
        
        # Create the database and tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT
        )
        ''')
        
        # Create posts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            body TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Insert mock data
        cursor.execute("DELETE FROM posts")
        cursor.execute("DELETE FROM users")
        
        users = [
            (1, "John Doe", "john@example.com"),
            (2, "Jane Smith", "jane@example.com"),
            (3, "Bob Johnson", "bob@example.com")
        ]
        
        posts = [
            (1, 1, "First Post", "This is the first post content"),
            (2, 1, "Second Post", "This is the second post content"),
            (3, 2, "Another Post", "This is another post content")
        ]
        
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", users)
        cursor.executemany("INSERT INTO posts VALUES (?, ?, ?, ?)", posts)
        
        conn.commit()
        conn.close()
        
        return {
            "fetch_users": {"users": 3},
            "fetch_posts": {"posts": 3},
            "store_data": {"users_stored": 3, "posts_stored": 3, "db_path": db_path},
            "generate_report": {"report": "Generated report with 3 users and 3 posts"}
        }
else:
    # Import real Taskinity functionality
    try:
        from taskinity.core.taskinity_core import task, run_flow_from_dsl
        import requests
    except ImportError:
        print("Error: Could not import Taskinity modules. Run with --mock flag for testing.")
        sys.exit(1)

@task(name="Fetch Users")
def fetch_users(api_url):
    print(f"Fetching users from {api_url}")
    response = requests.get(f"{api_url}/users")
    if response.status_code == 200:
        users = response.json().get("data", [])
        print(f"Fetched {len(users)} users")
        return {"users": users}
    else:
        print(f"Error fetching users: {response.status_code}")
        return {"users": []}

@task(name="Fetch Posts")
def fetch_posts(api_url):
    print(f"Fetching posts from {api_url}")
    response = requests.get(f"{api_url}/posts")
    if response.status_code == 200:
        posts = response.json().get("data", [])
        print(f"Fetched {len(posts)} posts")
        return {"posts": posts}
    else:
        print(f"Error fetching posts: {response.status_code}")
        return {"posts": []}

@task(name="Store Data")
def store_data(users_data, posts_data, db_path):
    print(f"Storing data to {db_path}")
    users = users_data.get("users", [])
    posts = posts_data.get("posts", [])
    
    # Create the database and tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )
    ''')
    
    # Create posts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        body TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Insert data
    for user in users:
        cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
                      (user["id"], user["name"], user["email"]))
    
    for post in posts:
        cursor.execute("INSERT OR REPLACE INTO posts VALUES (?, ?, ?, ?)",
                      (post["id"], post["user_id"], post["title"], post["body"]))
    
    conn.commit()
    conn.close()
    
    return {
        "users_stored": len(users),
        "posts_stored": len(posts),
        "db_path": db_path
    }

@task(name="Generate Report")
def generate_report(store_result):
    users_stored = store_result.get("users_stored", 0)
    posts_stored = store_result.get("posts_stored", 0)
    db_path = store_result.get("db_path", "")
    
    print(f"Generating report for {users_stored} users and {posts_stored} posts")
    
    # Connect to the database to generate a report
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get user post counts
    cursor.execute('''
    SELECT u.name, COUNT(p.id) as post_count
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    GROUP BY u.id
    ORDER BY post_count DESC
    ''')
    
    user_stats = cursor.fetchall()
    
    # Generate report
    report = f"API Data Report\n"
    report += f"==============\n\n"
    report += f"Total Users: {users_stored}\n"
    report += f"Total Posts: {posts_stored}\n\n"
    report += f"User Post Counts:\n"
    
    for user_name, post_count in user_stats:
        report += f"- {user_name}: {post_count} posts\n"
    
    conn.close()
    
    return {"report": report}

# Define the flow DSL
flow_dsl = """
flow APIIntegration:
    description: "API data integration flow"
    fetch_users -> store_data
    fetch_posts -> store_data
    store_data -> generate_report
"""

# Ensure the examples directory exists
os.makedirs("examples", exist_ok=True)

# Run the flow
results = run_flow_from_dsl(flow_dsl, {
    "api_url": "https://api.example.com",
    "db_path": "examples/api_data.db"
})

print("\nFlow results:")
print(f"Users fetched: {results['fetch_users'].get('users', 0)}")
print(f"Posts fetched: {results['fetch_posts'].get('posts', 0)}")
print(f"Data stored in: {results['store_data'].get('db_path', '')}")

# Print the report
print("\nGenerated Report:")
print(results['generate_report']['report'])
