from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Exam, Question, QuestionOption, Submission, Answer, ExamQuestion

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('id', 'text') # Exclude is_correct

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'options')

class ExamSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = ('id', 'title', 'course', 'description', 'duration_minutes', 'questions', 'created_at')
        
    def get_questions(self, obj):
        # Fetch via through-model to respect order
        exam_questions = ExamQuestion.objects.filter(exam=obj).select_related('question').prefetch_related('question__options')
        questions = [eq.question for eq in exam_questions]
        return QuestionSerializer(questions, many=True).data

class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option_id = serializers.IntegerField(required=False, allow_null=True)
    text_answer = serializers.CharField(required=False, allow_blank=True)

class SubmissionCreateSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    answers = AnswerInputSerializer(many=True)

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('id', 'exam', 'score', 'status', 'started_at', 'submitted_at')
