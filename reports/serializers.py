from rest_framework import serializers
from .models import RiskReport, ReportComment, Intervention, CollaborationNote
from students.models import Student
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'user_type', 'department']


class StudentSerializer(serializers.ModelSerializer):
    assigned_counselor_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_assigned_counselor_name(self, obj):
        if obj.assigned_counselor:
            return obj.assigned_counselor.get_full_name()
        return None


class ReportCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_type = serializers.SerializerMethodField()

    class Meta:
        model = ReportComment
        fields = '__all__'

    def get_author_name(self, obj):
        return obj.author.get_full_name()

    def get_author_type(self, obj):
        return obj.author.user_type


class InterventionSerializer(serializers.ModelSerializer):
    conducted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Intervention
        fields = '__all__'

    def get_conducted_by_name(self, obj):
        if obj.conducted_by:
            return obj.conducted_by.get_full_name()
        return None


class RiskReportSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_details = StudentSerializer(source='student', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    comments = ReportCommentSerializer(many=True, read_only=True)
    interventions = InterventionSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = RiskReport
        fields = '__all__'

    def get_student_name(self, obj):
        return obj.student.get_full_name()

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name()
        return None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None

    def get_comment_count(self, obj):
        return obj.comments.count()


class CollaborationNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    shared_with_details = UserSerializer(source='shared_with', many=True, read_only=True)

    class Meta:
        model = CollaborationNote
        fields = '__all__'

    def get_author_name(self, obj):
        return obj.author.get_full_name()

    def get_student_name(self, obj):
        return obj.student.get_full_name()