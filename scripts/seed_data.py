import os
import django
import sys

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Exam, Question

def seed():
    print("Seeding data...")
    if Exam.objects.filter(title="Professional Backend Assessment").exists():
        print("Exam already exists. Skipping.")
        return

    exam = Exam.objects.create(
        title="Professional Backend Assessment",
        description="A test of general backend knowledge.",
        duration_minutes=45
    )

    Question.objects.create(
        exam=exam,
        text="Which status code indicates a successful resource creation?",
        question_type='MCQ',
        options=["200", "201", "204", "500"],
        correct_answer="201"
    )

    Question.objects.create(
        exam=exam,
        text="What does ACID stand for in databases?",
        question_type='TEXT',
        correct_answer="Atomicity, Consistency, Isolation, Durability"
    )
    
    print(f"Created Exam: {exam.title} with 2 questions.")

if __name__ == '__main__':
    seed()
