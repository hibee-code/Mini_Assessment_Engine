from difflib import SequenceMatcher
from .models import Submission, Answer, Question

class MockGradingService:
    @staticmethod
    def grade_submission(submission_id):
        submission = Submission.objects.get(id=submission_id)
        answers = submission.answers.all()
        total_questions = submission.exam.questions.count()
        correct_count = 0
        
        for answer in answers:
            question = answer.question
            is_correct = False
            
            if question.question_type == 'MCQ':
                # Exact match for MCQ
                if answer.student_answer.strip().lower() == question.correct_answer.strip().lower():
                    is_correct = True
            elif question.question_type == 'TEXT':
                # Fuzzy match for Text (Mock AI)
                similarity = SequenceMatcher(None, answer.student_answer.lower(), question.correct_answer.lower()).ratio()
                if similarity > 0.8: # Threshold for correctness
                    is_correct = True
            
            answer.is_correct = is_correct
            answer.save()
            
            if is_correct:
                correct_count += 1
        
        # Calculate Score (Percentage)
        if total_questions > 0:
            score = (correct_count / total_questions) * 100
        else:
            score = 0
            
        submission.score = score
        submission.save()
        return score
