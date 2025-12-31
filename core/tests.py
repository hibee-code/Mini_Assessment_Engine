from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from core.models import Exam, Question, Submission, Answer

class AuthTests(APITestCase):
    def test_register_user(self):
        data = {'username': 'newuser', 'email': 'new@test.com', 'password': 'password123'}
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in response.data)
        self.assertFalse('password' in response.data)

    def test_register_duplicate_username(self):
        User.objects.create_user(username='dupuser', password='password123')
        data = {'username': 'dupuser', 'email': 'other@test.com', 'password': 'password123'}
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(username='loginuser', password='password123')
        data = {'username': 'loginuser', 'password': 'password123'}
        response = self.client.post(reverse('token_obtain_pair'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        User.objects.create_user(username='wronguser', password='password123')
        data = {'username': 'wronguser', 'password': 'wrongpassword'}
        response = self.client.post(reverse('token_obtain_pair'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ExamTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='examuser', password='password123')
        token_resp = self.client.post(reverse('token_obtain_pair'), {'username': 'examuser', 'password': 'password123'})
        self.token = token_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        self.exam = Exam.objects.create(title="Test Exam", duration_minutes=30)
        
    def test_list_exams_authenticated(self):
        response = self.client.get(reverse('exam-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_list_exams_unauthenticated(self):
        self.client.credentials() # Remove auth
        response = self.client.get(reverse('exam-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class SubmissionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='password123')
        token_resp = self.client.post(reverse('token_obtain_pair'), {'username': 'student', 'password': 'password123'})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_resp.data['access'])
        
        self.exam = Exam.objects.create(title="Math", duration_minutes=60)
        self.q_mcq = Question.objects.create(
            exam=self.exam, text="1+1?", question_type='MCQ', 
            options=["1", "2"], correct_answer="2"
        )
        self.q_text = Question.objects.create(
            exam=self.exam, text="Name a color", question_type='TEXT', 
            correct_answer="Blue"
        )

    def test_submit_valid_exam(self):
        data = {
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.q_mcq.id, 'student_answer': '2'},
                {'question_id': self.q_text.id, 'student_answer': 'Blue'}
            ]
        }
        response = self.client.post(reverse('submit_exam'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 100.0)
        
        # Verify DB
        submission = Submission.objects.get(id=response.data['id'])
        self.assertEqual(submission.answers.count(), 2)

    def test_submit_invalid_exam_id(self):
        data = {'exam_id': 9999, 'answers': []}
        response = self.client.post(reverse('submit_exam'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_submit_empty_answers(self):
        # Should still create submission but get 0 score
        data = {
            'exam_id': self.exam.id,
            'answers': []
        }
        response = self.client.post(reverse('submit_exam'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 0.0)

    def test_view_my_submissions(self):
        # Create a submission first
        sub = Submission.objects.create(student=self.user, exam=self.exam, score=85.0)
        
        response = self.client.get(reverse('my_submissions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['score'], 85.0)
        
    def test_cannot_view_others_submissions(self):
        other_user = User.objects.create_user(username='other', password='password123')
        Submission.objects.create(student=other_user, exam=self.exam, score=10.0)
        
        response = self.client.get(reverse('my_submissions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) # Should verify isolation
