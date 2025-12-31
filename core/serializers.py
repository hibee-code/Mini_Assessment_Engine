from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Exam, Question, Submission, Answer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'options') # Exclude correct_answer

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exam
        fields = ('id', 'title', 'description', 'duration_minutes', 'questions', 'created_at')

class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    student_answer = serializers.CharField()

class SubmissionCreateSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    answers = AnswerInputSerializer(many=True)

class SubmissionSerializer(serializers.ModelSerializer):
    score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Submission
        fields = ('id', 'exam', 'score', 'started_at', 'completed_at')
