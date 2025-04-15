# resume_analyzer/urls.py
from django.urls import path
from .views import ResumeAnalysisView, CoverLetterView

urlpatterns = [
    path('resume-analysis/', ResumeAnalysisView.as_view(), name='analyze-resume'),
    path('cover-letter/', CoverLetterView.as_view(), name='cover-letter'),
]