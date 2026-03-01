from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from .models import RiskReport, ReportComment, Intervention, CollaborationNote
from students.models import Student
from .serializers import (
    RiskReportSerializer, ReportCommentSerializer,
    InterventionSerializer, CollaborationNoteSerializer,
    StudentSerializer
)
from .ai_risk_detector import generate_risk_report


class RiskReportViewSet(viewsets.ModelViewSet):
    """ViewSet for risk reports"""
    
    queryset = RiskReport.objects.all()
    serializer_class = RiskReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RiskReport.objects.all()
        user = self.request.user

        # Filter by user type
        if user.user_type == 'counselor':
            # Counselors see reports for their assigned students or assigned to them
            queryset = queryset.filter(
                Q(student__assigned_counselor=user) | Q(assigned_to=user)
            )
        elif user.user_type == 'professor':
            # Professors see reports for students in their courses
            student_ids = user.courses.values_list('student_id', flat=True)
            queryset = queryset.filter(student_id__in=student_ids)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by risk level
        risk_level = self.request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)

        return queryset.select_related('student', 'created_by', 'assigned_to')

    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate AI risk report for a student"""
        student_id = request.data.get('student_id')

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate AI analysis
        analysis = generate_risk_report(student)

        # Create risk report
        report = RiskReport.objects.create(
            student=student,
            risk_level=analysis['risk_level'],
            risk_score=analysis['risk_score'],
            academic_risk=analysis['academic_risk'],
            attendance_risk=analysis['attendance_risk'],
            engagement_risk=analysis['engagement_risk'],
            behavioral_risk=analysis['behavioral_risk'],
            ai_summary=analysis['summary'],
            ai_indicators=analysis['indicators'],
            ai_recommendations=analysis['recommendations'],
            created_by=request.user,
            assigned_to=student.assigned_counselor
        )

        # Update student's overall risk score
        student.overall_risk_score = analysis['risk_score']
        student.last_risk_assessment = timezone.now()
        student.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add comment to a report"""
        report = self.get_object()

        comment = ReportComment.objects.create(
            report=report,
            author=request.user,
            content=request.data.get('content'),
            is_private=request.data.get('is_private', False)
        )

        serializer = ReportCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update report status"""
        report = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(RiskReport.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.status = new_status
        
        if new_status == 'reviewed':
            report.reviewed_at = timezone.now()
        elif new_status == 'resolved':
            report.resolved_at = timezone.now()

        report.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data)


class InterventionViewSet(viewsets.ModelViewSet):
    """ViewSet for interventions"""
    
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Intervention.objects.all()
        user = self.request.user

        # Filter by user
        if user.user_type != 'admin':
            queryset = queryset.filter(conducted_by=user)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('report', 'conducted_by')


class CollaborationNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for collaboration notes"""
    
    queryset = CollaborationNote.objects.all()
    serializer_class = CollaborationNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CollaborationNote.objects.all()
        user = self.request.user

        # Users see notes they created or that are shared with them
        queryset = queryset.filter(
            Q(author=user) | Q(shared_with=user) | Q(is_private=False)
        ).distinct()

        # Filter by student
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        return queryset.select_related('student', 'author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet for students"""
    
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Student.objects.all()
        user = self.request.user

        # Filter by user type
        if user.user_type == 'counselor':
            queryset = queryset.filter(assigned_counselor=user)
        elif user.user_type == 'professor':
            student_ids = user.courses.values_list('student_id', flat=True)
            queryset = queryset.filter(id__in=student_ids)

        # Filter by risk level
        risk_filter = self.request.query_params.get('risk')
        if risk_filter == 'high':
            queryset = queryset.filter(overall_risk_score__gte=0.5)
        elif risk_filter == 'medium':
            queryset = queryset.filter(
                overall_risk_score__gte=0.3,
                overall_risk_score__lt=0.5
            )

        return queryset.select_related('assigned_counselor')

    @action(detail=True, methods=['get'])
    def risk_history(self, request, pk=None):
        """Get risk report history for a student"""
        student = self.get_object()
        reports = RiskReport.objects.filter(student=student).order_by('-created_at')
        serializer = RiskReportSerializer(reports, many=True)
        return Response(serializer.data)

