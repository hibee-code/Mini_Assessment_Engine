from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
    title = models.CharField(max_length=255)
    course = models.CharField(max_length=255, help_text="Course/Subject Name")
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    metadata = models.JSONField(default=dict, blank=True, help_text="Extra settings like difficulty, tags")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course}: {self.title}"

class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice'),
        ('TEXT', 'Text Answer'),
    )

    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    # expected_answer is mainly for TEXT or simple matching. 
    # For MCQ, the correctness is in QuestionOption.
    expected_answer = models.TextField(blank=True, help_text="For TEXT questions or fallback")

    def __str__(self):
        return self.text[:50]

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id} -Option: {self.text}"

class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, related_name='exam_questions', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='exam_questions', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('exam', 'question')
        ordering = ['order']

class Submission(models.Model):
    STATUS_CHOICES = (
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('GRADED', 'Graded'),
    )

    student = models.ForeignKey(User, related_name='submissions', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, related_name='submissions', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    score = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Enforce one submission per exam per student (as per security requirements)
        # Note: In a real app we might want 'attempts', but 'Mini Assessment' usually implies single shot.
        # We can relax this if multiple attempts are needed, but this constraint is solid for "Secure".
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

class Answer(models.Model):
    submission = models.ForeignKey(Submission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    selected_option = models.ForeignKey(
        QuestionOption, null=True, blank=True, on_delete=models.SET_NULL, related_name='answers'
    )
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True)

    def __str__(self):
        return f"Ans: {self.question.id} by {self.submission.student.username}"
