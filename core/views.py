from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Exam, Question, Submission, Answer, QuestionOption, ExamQuestion
from .serializers import UserSerializer, ExamSerializer, SubmissionCreateSerializer, SubmissionSerializer
from .services import MockGradingService
from drf_spectacular.utils import extend_schema

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(summary="Register a new student", responses={201: UserSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    # Prefetch through the junction table to get questions + options
    queryset = Exam.objects.all() # Optimization handled in Serializer get_questions via specific query
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
        description="Submit answers. For MCQ, provide `selected_option_id`. For Text, provide `text_answer`.",
        request=SubmissionCreateSerializer, 
        responses={201: SubmissionSerializer}
    )
    def post(self, request):
        serializer = SubmissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            exam = get_object_or_404(Exam, id=data['exam_id'])
            
            # Check for existing submission to enforce constraints
            if Submission.objects.filter(student=request.user, exam=exam).exists():
                return Response({"error": "You have already submitted this exam."}, status=status.HTTP_409_CONFLICT)
            
            # Create Submission (IN_PROGRESS)
            submission = Submission.objects.create(
                student=request.user,
                exam=exam,
                status='SUBMITTED' # Immediately submitted in this flow
            )
            
            answers_data = data['answers']
            new_answers = []
            
            # Fetch valid questions for this exam
            valid_questions = ExamQuestion.objects.filter(exam=exam).values_list('question_id', flat=True)
            valid_q_set = set(valid_questions)

            for ans in answers_data:
                q_id = ans['question_id']
                if q_id not in valid_q_set:
                     return Response({"error": f"Question {q_id} is not part of this exam"}, status=400)
                
                selected_opt = None
                if ans.get('selected_option_id'):
                    selected_opt = get_object_or_404(QuestionOption, id=ans['selected_option_id'])
                    # Verify option belongs to question
                    if selected_opt.question_id != q_id:
                        return Response({"error": f"Option {selected_opt.id} does not belong to Question {q_id}"}, status=400)

                new_answers.append(Answer(
                    submission=submission,
                    question_id=q_id,
                    selected_option=selected_opt,
                    text_answer=ans.get('text_answer', '')
                ))
            
            Answer.objects.bulk_create(new_answers)
            
            # Grade
            MockGradingService.grade_submission(submission.id)
            submission.refresh_from_db()
            
            return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MySubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user)
