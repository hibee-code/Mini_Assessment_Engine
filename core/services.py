from difflib import SequenceMatcher
from django.utils import timezone
from .models import Submission, Answer, QuestionOption

class MockGradingService:
    @staticmethod
    def grade_submission(submission_id):
        submission = Submission.objects.get(id=submission_id)
        
        # Ensure we are linking via the new junction table if needed, 
        # but for grading we just check the Submission->Answer relations.
        answers = submission.answers.all()
        # Correctly counting total questions from the junction table
        total_questions = submission.exam.exam_questions.count()
        correct_count = 0
        
        for answer in answers:
            question = answer.question
            is_correct = False
            
            if question.question_type == 'MCQ':
                # Senior-level logic: Check the boolean flag on the Foreign Key
                if answer.selected_option and answer.selected_option.is_correct:
                    is_correct = True
                    
            elif question.question_type == 'TEXT':
                # Fuzzy match for Text
                # Compare student input vs expected_answer text on Question model
                similarity = SequenceMatcher(None, answer.text_answer.lower(), question.expected_answer.lower()).ratio()
                if similarity > 0.8: 
                    is_correct = True
            
            answer.is_correct = is_correct
            answer.save()
            
            if is_correct:
                correct_count += 1
        
        # Calculate Score
        if total_questions > 0:
            score = (correct_count / total_questions) * 100
        else:
            score = 0
            
        submission.score = score
        submission.status = 'GRADED'
        submission.submitted_at = timezone.now()
        submission.save()
        return score
