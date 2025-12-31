from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import RegisterView, ExamViewSet, SubmitExamView, MySubmissionsView

router = DefaultRouter()
router.register(r'exams', ExamViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Core
    path('api/', include(router.urls)),
    path('api/submit/', SubmitExamView.as_view(), name='submit_exam'),
    path('api/my-submissions/', MySubmissionsView.as_view(), name='my_submissions'),
    
    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
