import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count
from students.models import Student, CourseEnrollment, StudentActivity


class AIRiskDetector:
    """AI service for detecting student risk factors"""

    def __init__(self, student):
        self.student = student
        self.risk_factors = {}
        self.indicators = {}

    def analyze_student(self):
        """Comprehensive student risk analysis"""

        # Calculate individual risk components
        academic_risk = self.calculate_academic_risk()
        attendance_risk = self.calculate_attendance_risk()
        engagement_risk = self.calculate_engagement_risk()
        behavioral_risk = self.calculate_behavioral_risk()

        # Calculate overall risk score (weighted average)
        overall_risk = (
            academic_risk * 0.35 +
            attendance_risk * 0.25 +
            engagement_risk * 0.25 +
            behavioral_risk * 0.15
        )

        # Determine risk level
        risk_level = self.determine_risk_level(overall_risk)

        # Generate AI summary and recommendations
        summary = self.generate_summary(overall_risk, risk_level)
        recommendations = self.generate_recommendations()

        return {
            'risk_score': round(overall_risk, 2),
            'risk_level': risk_level,
            'academic_risk': round(academic_risk, 2),
            'attendance_risk': round(attendance_risk, 2),
            'engagement_risk': round(engagement_risk, 2),
            'behavioral_risk': round(behavioral_risk, 2),
            'summary': summary,
            'recommendations': recommendations,
            'indicators': self.indicators
        }

    def calculate_academic_risk(self):
        """Calculate academic performance risk"""
        risk_score = 0.0
        indicators = []

        # GPA analysis
        if self.student.gpa:
            if self.student.gpa < 2.0:
                risk_score += 0.4
                indicators.append(f"GPA critically low: {self.student.gpa}")
            elif self.student.gpa < 2.5:
                risk_score += 0.25
                indicators.append(f"GPA below average: {self.student.gpa}")
            elif self.student.gpa < 3.0:
                risk_score += 0.1
                indicators.append(f"GPA needs improvement: {self.student.gpa}")

        # Course performance analysis
        enrollments = CourseEnrollment.objects.filter(
            student=self.student,
            is_active=True
        )

        failing_courses = enrollments.filter(current_grade__in=['D', 'F']).count()
        total_courses = enrollments.count()

        if total_courses > 0:
            failing_rate = failing_courses / total_courses
            if failing_rate > 0.5:
                risk_score += 0.3
                indicators.append(f"Failing {failing_courses}/{total_courses} courses")
            elif failing_rate > 0.25:
                risk_score += 0.15
                indicators.append(f"Struggling in {failing_courses}/{total_courses} courses")

            # Assignment completion
            avg_completion = enrollments.aggregate(
                avg_rate=Avg('assignments_completed') / Avg('assignments_total')
            )['avg_rate'] or 0

            if avg_completion < 0.5:
                risk_score += 0.2
                indicators.append(f"Low assignment completion: {avg_completion*100:.1f}%")
            elif avg_completion < 0.75:
                risk_score += 0.1
                indicators.append(f"Below average completion: {avg_completion*100:.1f}%")

        self.indicators['academic'] = indicators
        return min(risk_score, 1.0)

    def calculate_attendance_risk(self):
        """Calculate attendance-based risk"""
        risk_score = 0.0
        indicators = []

        enrollments = CourseEnrollment.objects.filter(
            student=self.student,
            is_active=True
        )

        if enrollments.exists():
            avg_attendance = enrollments.aggregate(
                avg=Avg('attendance_rate')
            )['avg'] or 100.0

            if avg_attendance < 60:
                risk_score = 0.9
                indicators.append(f"Critical attendance issue: {avg_attendance:.1f}%")
            elif avg_attendance < 75:
                risk_score = 0.6
                indicators.append(f"Poor attendance: {avg_attendance:.1f}%")
            elif avg_attendance < 85:
                risk_score = 0.3
                indicators.append(f"Attendance below threshold: {avg_attendance:.1f}%")

            # Check for recent attendance drop
            recent_attendance = enrollments.filter(
                enrolled_date__gte=timezone.now() - timedelta(days=30)
            ).aggregate(avg=Avg('attendance_rate'))['avg']

            if recent_attendance and recent_attendance < avg_attendance - 15:
                risk_score += 0.2
                indicators.append("Significant recent attendance decline")

        self.indicators['attendance'] = indicators
        return min(risk_score, 1.0)

    def calculate_engagement_risk(self):
        """Calculate student engagement risk"""
        risk_score = 0.0
        indicators = []

        # Check recent activities
        recent_activities = StudentActivity.objects.filter(
            student=self.student,
            date__gte=timezone.now() - timedelta(days=30)
        )

        activity_count = recent_activities.count()
        if activity_count < 5:
            risk_score += 0.4
            indicators.append(f"Very low engagement: {activity_count} activities in 30 days")
        elif activity_count < 10:
            risk_score += 0.2
            indicators.append(f"Low engagement: {activity_count} activities in 30 days")

        # Participation analysis
        participation_activities = recent_activities.filter(
            activity_type='participation'
        )

        if participation_activities.exists():
            avg_score = participation_activities.aggregate(
                avg=Avg('score')
            )['avg'] or 0

            if avg_score < 60:
                risk_score += 0.3
                indicators.append(f"Low participation scores: {avg_score:.1f}%")

        self.indicators['engagement'] = indicators
        return min(risk_score, 1.0)

    def calculate_behavioral_risk(self):
        """Calculate behavioral risk indicators"""
        risk_score = 0.0
        indicators = []

        # Check for missing assignments pattern
        enrollments = CourseEnrollment.objects.filter(
            student=self.student,
            is_active=True
        )

        for enrollment in enrollments:
            if enrollment.assignments_total > 0:
                completion_rate = enrollment.assignments_completed / enrollment.assignments_total
                if completion_rate < 0.5 and enrollment.assignments_total >= 5:
                    risk_score += 0.15
                    indicators.append(f"Pattern of missed assignments in {enrollment.course_code}")

        # Check for grade drops
        if self.student.gpa and self.student.gpa < 2.5:
            recent_grades = enrollments.filter(
                current_grade__in=['D', 'F', 'W']
            ).count()
            if recent_grades > 0:
                risk_score += 0.2
                indicators.append(f"Recent poor performance in {recent_grades} courses")

        self.indicators['behavioral'] = indicators
        return min(risk_score, 1.0)

    def determine_risk_level(self, risk_score):
        """Determine risk level based on score"""
        if risk_score >= 0.75:
            return 'critical'
        elif risk_score >= 0.5:
            return 'high'
        elif risk_score >= 0.3:
            return 'medium'
        else:
            return 'low'

    def generate_summary(self, risk_score, risk_level):
        """Generate AI summary of risk assessment"""

        student_name = self.student.get_full_name()
        student_id = self.student.student_id

        if risk_level == 'critical':
            summary = f"CRITICAL ALERT: Student {student_name} ({student_id}) requires immediate intervention. "
            summary += f"Risk score of {risk_score:.2f} indicates severe academic and/or attendance issues. "
        elif risk_level == 'high':
            summary = f"HIGH RISK: Student {student_name} ({student_id}) is at significant risk. "
            summary += f"Risk score of {risk_score:.2f} shows multiple concerning factors. "
        elif risk_level == 'medium':
            summary = f"MODERATE CONCERN: Student {student_name} ({student_id}) shows some warning signs. "
            summary += f"Risk score of {risk_score:.2f} suggests early intervention may be beneficial. "
        else:
            summary = f"Student {student_name} ({student_id}) appears to be performing adequately. "
            summary += f"Risk score of {risk_score:.2f} is within acceptable range. "

        # Add key indicators
        all_indicators = []
        for category, indicators in self.indicators.items():
            all_indicators.extend(indicators)

        if all_indicators:
            summary += "Key indicators: " + "; ".join(all_indicators[:3]) + "."

        return summary

    def generate_recommendations(self):
        """Generate AI-powered recommendations"""

        recommendations = []

        # Academic recommendations
        if self.indicators.get('academic'):
            if 'GPA critically low' in str(self.indicators['academic']):
                recommendations.append("URGENT: Schedule immediate academic counseling session")
                recommendations.append("Consider reduced course load for next semester")
                recommendations.append("Refer to tutoring services for struggling courses")
            elif 'Failing' in str(self.indicators['academic']):
                recommendations.append("Schedule meeting with professors for failing courses")
                recommendations.append("Develop academic improvement plan")
                recommendations.append("Connect with peer tutoring resources")

        # Attendance recommendations
        if self.indicators.get('attendance'):
            if 'Critical attendance' in str(self.indicators['attendance']):
                recommendations.append("URGENT: Meet with student to identify attendance barriers")
                recommendations.append("Contact emergency contact if student is unreachable")
            else:
                recommendations.append("Discuss attendance patterns and potential obstacles")
                recommendations.append("Provide flexible attendance options if appropriate")

        # Engagement recommendations
        if self.indicators.get('engagement'):
            recommendations.append("Increase check-ins and personal outreach")
            recommendations.append("Explore extracurricular activities or clubs")
            recommendations.append("Assess mental health and wellness needs")

        # Behavioral recommendations
        if self.indicators.get('behavioral'):
            recommendations.append("Conduct comprehensive student interview")
            recommendations.append("Assess for personal/family issues affecting performance")
            recommendations.append("Consider referral to campus counseling services")

        # Default recommendations
        if not recommendations:
            recommendations.append("Continue monitoring student progress")
            recommendations.append("Maintain regular check-in schedule")

        return "\n".join(f"• {rec}" for rec in recommendations)


def generate_risk_report(student):
    """Main function to generate risk report for a student"""

    detector = AIRiskDetector(student)
    analysis = detector.analyze_student()

    return analysis