import requests
import random
import string
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_e2e_test():
    print(">>> Starting E2E Orchestration <<<\n")
    
    # 1. Register User
    username = f"user_{generate_random_string()}"
    password = "SecurePassword123!"
    email = f"{username}@example.com"
    
    print(f"[1] Registering User: {username}")
    resp = requests.post(f"{BASE_URL}/auth/register/", json={
        "username": username,
        "email": email,
        "password": password
    })
    if resp.status_code == 201:
        print("    Success: User created.")
    else:
        print(f"    Failed: {resp.text}")
        return

    # 2. Login
    print(f"[2] Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": username,
        "password": password
    })
    if resp.status_code == 200:
        token = resp.json()['access']
        print("    Success: Token acquired.")
    else:
        print(f"    Failed: {resp.text}")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. List Exams
    print(f"[3] Fetching Exams...")
    resp = requests.get(f"{BASE_URL}/exams/", headers=headers)
    exams = resp.json()
    if len(exams) > 0:
        exam = exams[0]
        print(f"    Found Exam: '{exam['title']}' (ID: {exam['id']})")
    else:
        print("    Failed: No exams found. Did you run the seed script?")
        return
        
    # 4. Take Exam (Prepare Answers)
    print(f"[4] Solving Exam...")
    questions = exam['questions']
    answers = []
    
    for q in questions:
        q_id = q['id']
        q_text = q['text']
        print(f"    Question: {q_text}")
        
        # Simple logic to answer based on known seed data
        ans = ""
        if "status code" in q_text:
            ans = "201"
        elif "ACID" in q_text:
            ans = "Atomicity, Consistency, Isolation, Durability" # Exact match for max score
        else:
            ans = "Unknown"
            
        print(f"    -> Answering: {ans}")
        answers.append({"question_id": q_id, "student_answer": ans})
        
    # 5. Submit
    print(f"[5] Submitting Answers...")
    payload = {
        "exam_id": exam['id'],
        "answers": answers
    }
    resp = requests.post(f"{BASE_URL}/submit/", json=payload, headers=headers)
    
    if resp.status_code == 201:
        result = resp.json()
        print(f"    Success: Submission received.")
        print(f"\n>>> FINAL GRADE: {result['score']}% <<<")
        
        if result['score'] == 100:
            print("    PERFECT SCORE! The mock AI grader validated the answers accurately.")
        else:
            print("    Score was less than 100%. Check grading logic or fuzzy match sensitivity.")
    else:
        print(f"    Failed: {resp.text}")

if __name__ == "__main__":
    try:
        run_e2e_test()
    except Exception as e:
        print(f"An error occurred: {e}")
