# resume_analyzer/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import google.generativeai as genai
import os
from .prompts import input_prompt1, resume_tailor_prompt, input_prompt3, input_prompt4, resume_analysis_prompt, cover_letter_prompt
from dotenv import load_dotenv
import os
from PIL import Image
import io
import pdf2image
import base64
import fitz

import google.generativeai as genai

# Configure Gemini AI
load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY') # getting the api key from os.getenv
genai.configure(api_key=os.getenv(API_KEY))

class ResumeAnalysisView(APIView):
    # Add parsers to handle file uploads
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        # Extract the file and job description from the request
        uploaded_file = request.FILES.get('uploaded_file')
        job_description = request.data.get('job_description')
        action = request.query_params.get('action', '')
        
        if not uploaded_file:
            return Response({"error": 'file is required.'})
        if action and (not job_description):
            return Response({"error": 'job description is required.'})
        try:
            # Process the PDF file
            pdf_content = self.input_pdf_setup(uploaded_file)
            # Get Gemini response based on the action
            response = self.get_response_based_on_action(action, pdf_content, job_description)
            return Response({"response": response}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def input_pdf_setup(self, uploaded_file):
        if uploaded_file:
            document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text_parts = []
            for page in document:
                text_parts.append(page.get_text())
            pdf_text_content = " ".join(text_parts)
            return pdf_text_content
        else:
            raise FileNotFoundError("No file uploaded")

    def get_gemini_response(self, prompt, pdf_content, input):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, pdf_content, input])
        return response.text
    
    def get_response_based_on_action(self, action, pdf_content, job_description):
        if action:
            if action == 'missing-keywords':
                return self.get_gemini_response(input_prompt3, pdf_content, job_description)
            elif action == 'percentage-match':
                return self.get_gemini_response(input_prompt4, pdf_content, job_description)
            elif action == "improvise-skills":
                return self.get_gemini_response(resume_tailor_prompt, pdf_content, job_description)
        else:
            return self.get_gemini_response(resume_analysis_prompt, pdf_content, "")
    
    def list_available_models(self):
        models = genai.list_models()
        model_list = []
        for model in models:
            model_info = {
                "name": model.name,
                "description": model.description,
                "supported_generation_methods": model.supported_generation_methods,
            }
            model_list.append(model_info)
        return model_list
    
    
class CoverLetterView(ResumeAnalysisView):
    def post(self, request, *args, **kwargs):
        # Extract the file and job description from the request
        uploaded_file = request.FILES.get('uploaded_file')
        job_description = request.data.get('job_description')
        
        if not uploaded_file:
            return Response({"error": 'file is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not job_description:
            return Response({"error": 'job description is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Process the PDF file
            pdf_content = self.input_pdf_setup(uploaded_file)
            # Get Gemini response for cover letter
            response = self.get_gemini_response(cover_letter_prompt, pdf_content, job_description)
            return Response({"response": response}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)