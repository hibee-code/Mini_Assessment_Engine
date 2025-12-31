from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TEXT', 'Text Answer'),
    ]
    
    exam = models.ForeignKey(Exam, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='MCQ')
    options = models.JSONField(blank=True, null=True, help_text="JSON list of options for MCQ")
    correct_answer = models.TextField(help_text="The correct answer string")
    
    def __str__(self):
        return f"{self.exam.title} - {self.text[:50]}"

class Submission(models.Model):
    student = models.ForeignKey(User, related_name='submissions', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, related_name='submissions', on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

class Answer(models.Model):
    submission = models.ForeignKey(Submission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    student_answer = models.TextField()
    is_correct = models.BooleanField(null=True)
    
    def __str__(self):
        return f"Ans: {self.question.id} by {self.submission.student.username}"
