from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from core.models import Exam, Question, QuestionOption, ExamQuestion, Submission

class AuthTests(APITestCase):
    def test_register_user(self):
        data = {'username': 'newuser', 'email': 'new@test.com', 'password': 'password123'}
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class SeniorArchitectureTests(APITestCase):
    def setUp(self):
        # User
        self.user = User.objects.create_user(username='student', password='password123')
        token_resp = self.client.post(reverse('token_obtain_pair'), {'username': 'student', 'password': 'password123'})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_resp.data['access'])
        
        # Exam
        self.exam = Exam.objects.create(title="Advanced DB", course="CS500", duration_minutes=60)
        
        # Question 1: MCQ
        self.q1 = Question.objects.create(text="Select the correct AC property?", question_type='MCQ')
        self.opt1_correct = QuestionOption.objects.create(question=self.q1, text="Atomicity", is_correct=True)
        self.opt1_wrong = QuestionOption.objects.create(question=self.q1, text="Apple", is_correct=False)
        
        # Question 2: Text
        self.q2 = Question.objects.create(text="Define index.", question_type='TEXT', expected_answer="A data structure to improve retrieval speed.")
        
        # Link via Junction
        ExamQuestion.objects.create(exam=self.exam, question=self.q1, order=1)
        ExamQuestion.objects.create(exam=self.exam, question=self.q2, order=2)

    def test_exam_list_structure(self):
        response = self.client.get(reverse('exam-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check nested structure
        data = response.data[0]
        self.assertEqual(data['title'], "Advanced DB")
        self.assertEqual(len(data['questions']), 2)
        # Check Q1 options
        q1_data = next(q for q in data['questions'] if q['id'] == self.q1.id)
        self.assertEqual(len(q1_data['options']), 2)

    def test_submission_grading_success(self):
        data = {
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.q1.id, 'selected_option_id': self.opt1_correct.id},
                {'question_id': self.q2.id, 'text_answer': "A data structure to improve retrieval speed."}
            ]
        }
        response = self.client.post(reverse('submit_exam'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 100.0)
        
        # Verify DB Status
        sub = Submission.objects.get(id=response.data['id'])
        self.assertEqual(sub.status, 'GRADED')

    def test_submission_validation_wrong_option(self):
        # Trying to submit an option that doesn't belong to the question
        other_q = Question.objects.create(text="Dummy", question_type='MCQ')
        other_opt = QuestionOption.objects.create(question=other_q, text="Trap", is_correct=True)
        
        data = {
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.q1.id, 'selected_option_id': other_opt.id}
            ]
        }
        response = self.client.post(reverse('submit_exam'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submission_duplicate_prevention(self):
        # Submit once
        self.test_submission_grading_success()
        
        # Try again
        data = {'exam_id': self.exam.id, 'answers': []}
        response = self.client.post(reverse('submit_exam'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
