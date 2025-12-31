from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Exam, Question, Submission, Answer
from .serializers import UserSerializer, ExamSerializer, SubmissionCreateSerializer, SubmissionSerializer
from .services import MockGradingService
from drf_spectacular.utils import extend_schema

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register a new student",
        responses={201: UserSerializer, 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(summary="List available exams")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @extend_schema(summary="Retrieve exam details")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class SubmitExamView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Submit an exam",
        description="Submit answers for an exam. Grading is instant.",
        request=SubmissionCreateSerializer, 
        responses={
            201: SubmissionSerializer, 
            400: "Validation Error",
            404: "Exam or Question not found"
        }
    )
    def post(self, request):
        serializer = SubmissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            exam = get_object_or_404(Exam, id=data['exam_id'])
            
            # Prevent duplicate submissions? (Optional logic, skipping for simple task)
            
            submission = Submission.objects.create(
                student=request.user,
                exam=exam
            )
            
            answers_data = data['answers']
            new_answers = []
            for ans in answers_data:
                question = get_object_or_404(Question, id=ans['question_id'])
                new_answers.append(Answer(
                    submission=submission,
                    question=question,
                    student_answer=ans['student_answer']
                ))
            
            Answer.objects.bulk_create(new_answers)
            
            # Trigger Grading
            MockGradingService.grade_submission(submission.id)
            submission.refresh_from_db()
            
            return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MySubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user)
