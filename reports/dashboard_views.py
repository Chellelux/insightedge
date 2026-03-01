from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from .models import RiskReport, Intervention
from students.models import Student, CourseEnrollment
from analytics.models import AnalyticsDashboard
from datetime import datetime, timedelta
from django.utils import timezone


@login_required
def dashboard(request):
    """Main dashboard view"""

    user = request.user
    today = timezone.now().date()

    # Get students based on user type
    if user.user_type == 'counselor':
        students = Student.objects.filter(assigned_counselor=user)
        reports = RiskReport.objects.filter(
            Q(student__assigned_counselor=user) | Q(assigned_to=user)
        )
    elif user.user_type == 'professor':
        student_ids = user.courses.values_list('student_id', flat=True)
        students = Student.objects.filter(id__in=student_ids)
        reports = RiskReport.objects.filter(student_id__in=student_ids)
    else:
        students = Student.objects.all()
        reports = RiskReport.objects.all()

    # Calculate statistics
    total_students = students.count()
    at_risk_students = students.filter(overall_risk_score__gte=0.3).count()
    high_risk_students = students.filter(overall_risk_score__gte=0.5).count()
    critical_risk_students = students.filter(overall_risk_score__gte=0.75).count()

    # Recent reports
    recent_reports = reports.order_by('-created_at')[:5]
    pending_reports = reports.filter(status='pending').count()

    # Interventions
    interventions = Intervention.objects.filter(report__in=reports)
    pending_interventions = interventions.filter(status='scheduled').count()

    context = {
        'total_students': total_students,
        'at_risk_students': at_risk_students,
        'high_risk_students': high_risk_students,
        'critical_risk_students': critical_risk_students,
        'recent_reports': recent_reports,
        'pending_reports': pending_reports,
        'pending_interventions': pending_interventions,
    }

    return render(request, 'dashboard.html', context)


@login_required
def student_list(request):
    """Student list view"""

    user = request.user

    if user.user_type == 'counselor':
        students = Student.objects.filter(assigned_counselor=user)
    elif user.user_type == 'professor':
        student_ids = user.courses.values_list('student_id', flat=True)
        students = Student.objects.filter(id__in=student_ids)
    else:
        students = Student.objects.all()

    # Filter by risk level
    risk_filter = request.GET.get('risk')
    if risk_filter == 'high':
        students = students.filter(overall_risk_score__gte=0.5)
    elif risk_filter == 'medium':
        students = students.filter(overall_risk_score__gte=0.3, overall_risk_score__lt=0.5)
    elif risk_filter == 'low':
        students = students.filter(overall_risk_score__lt=0.3)

    # Search
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(student_id__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )

    students = students.select_related('assigned_counselor').order_by('-overall_risk_score')

    context = {
        'students': students,
        'risk_filter': risk_filter,
        'search': search,
    }

    return render(request, 'student_list.html', context)


@login_required
def student_detail(request, pk):
    """Student detail view"""

    student = get_object_or_404(Student, pk=pk)

    # Get student's reports
    reports = RiskReport.objects.filter(student=student).order_by('-created_at')

    # Get enrollments
    enrollments = CourseEnrollment.objects.filter(student=student, is_active=True)

    # Get interventions
    interventions = Intervention.objects.filter(
        report__student=student
    ).order_by('-scheduled_date')

    context = {
        'student': student,
        'reports': reports,
        'enrollments': enrollments,
        'interventions': interventions,
    }

    return render(request, 'student_detail.html', context)


@login_required
def report_list(request):
    """Report list view"""

    user = request.user

    if user.user_type == 'counselor':
        reports = RiskReport.objects.filter(
            Q(student__assigned_counselor=user) | Q(assigned_to=user)
        )
    elif user.user_type == 'professor':
        student_ids = user.courses.values_list('student_id', flat=True)
        reports = RiskReport.objects.filter(student_id__in=student_ids)
    else:
        reports = RiskReport.objects.all()

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)

    # Filter by risk level
    risk_level = request.GET.get('risk_level')
    if risk_level:
        reports = reports.filter(risk_level=risk_level)

    reports = reports.select_related('student', 'created_by', 'assigned_to').order_by('-created_at')

    context = {
        'reports': reports,
        'status_filter': status_filter,
        'risk_level': risk_level,
    }

    return render(request, 'report_list.html', context)


@login_required
def report_detail(request, pk):
    """Report detail view"""

    report = get_object_or_404(RiskReport, pk=pk)

    # Get comments and interventions
    comments = report.comments.select_related('author').all()
    interventions = report.interventions.select_related('conducted_by').all()

    context = {
        'report': report,
        'comments': comments,
        'interventions': interventions,
    }

    return render(request, 'report_detail.html', context)


@login_required
def analytics(request):
    """Analytics dashboard view"""

    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    # Get all students
    total_students = Student.objects.count()
    at_risk_students = Student.objects.filter(overall_risk_score__gte=0.3).count()

    # Get reports statistics
    reports = RiskReport.objects.filter(
        created_at__date__gte=start_date
    )

    reports_by_level = reports.values('risk_level').annotate(count=Count('id'))
    reports_by_status = reports.values('status').annotate(count=Count('id'))

    # Get intervention statistics
    interventions = Intervention.objects.filter(
        scheduled_date__date__gte=start_date
    )

    interventions_by_type = interventions.values('intervention_type').annotate(count=Count('id'))
    interventions_by_status = interventions.values('status').annotate(count=Count('id'))

    # Average metrics
    avg_gpa = Student.objects.aggregate(avg=Avg('gpa'))['avg'] or 0
    avg_risk_score = Student.objects.aggregate(avg=Avg('overall_risk_score'))['avg'] or 0

    context = {
        'total_students': total_students,
        'at_risk_students': at_risk_students,
        'reports_by_level': list(reports_by_level),
        'reports_by_status': list(reports_by_status),
        'interventions_by_type': list(interventions_by_type),
        'interventions_by_status': list(interventions_by_status),
        'avg_gpa': round(avg_gpa, 2),
        'avg_risk_score': round(avg_risk_score, 2),
    }

    return render(request, 'analytics.html', context)