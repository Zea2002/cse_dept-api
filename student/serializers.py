from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Semester, Batch, Student, Routine, Subject, Registration, Result, Announcement
from rest_framework import serializers
from .models import Semester, Batch,  Student, Routine, Subject, Registration, Result, Announcement
from  user.models import User
from django.contrib.auth.hashers import check_password


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'name', 'start_date', 'end_date', 'year']


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'name']



class StudentSerializer(serializers.ModelSerializer):
    # Nested serializers for User-related data
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    Batch_name=serializers.CharField(source='batch.name', read_only=True)
    username=serializers.CharField(source="user.username",read_only=True)
    role=serializers.CharField(source="user.role",read_only=True)

    class Meta:
        model = Student
        fields = [
            # User-related fields
            'id', 'first_name', 'last_name', 'email','username','role','password',
            
            # Personal details
            'phone', 'date_of_birth', 'address', 'gender', 'photo',
            'father_name', 'mother_name',

            # Batch and status
            'batch', 'is_approved', 'student_id','Batch_name',

            # SSC details
            'ssc_roll', 'ssc_reg', 'ssc_passing_year', 'ssc_result',
            'ssc_school', 'ssc_board', 'ssc_group',

            # HSC details
            'hsc_roll', 'hsc_reg', 'hsc_passing_year', 'hsc_result',
            'hsc_college', 'hsc_board', 'hsc_group',
        ]
        read_only_fields = ['student_id', 'is_approved']  # Mark fields as read-only if necessary


class StudentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Student, including creating the associated User object.
    """
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    
    username=serializers.CharField(source="user.username")

    class Meta:
        model = Student
        fields = [
            # User-related fields
            'first_name', 'last_name', 'email','username',
            
            # Personal details
            'phone', 'date_of_birth', 'address', 'gender', 'photo',
            'father_name', 'mother_name',

            # Batch and SSC/HSC details
            'batch', 'ssc_roll', 'ssc_reg', 'ssc_passing_year', 'ssc_result',
            'ssc_school', 'ssc_board', 'ssc_group',
            'hsc_roll', 'hsc_reg', 'hsc_passing_year', 'hsc_result',
            'hsc_college', 'hsc_board', 'hsc_group',
        ]

    def create(self, validated_data):
        # Extract user data
        user_data = validated_data.pop('user')
        user = User.objects.create(
            username=user_data['username'],  # Assuming email is used as the username
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
        )
        user.set_password('defaultpassword')  # Set a default password or use email for verification
        user.save()

        # Create the student object
        student = Student.objects.create(user=user, **validated_data)
        return student



class RoutineSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.name', read_only=True) 
    class Meta:
        model = Routine
        fields = ['id', 'batch', 'batch_name', 'file']




class SubjectSerializer(serializers.ModelSerializer):
    total_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'course_title', 'course_code', 'credit', 'credit_fee', 'total_fee']


class RegistrationSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())
    courses = serializers.PrimaryKeyRelatedField(many=True, queryset=Subject.objects.all())
    total_fee = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    coures_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    semester_name = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = ['id', 'student', 'semester', 'courses', 'semester_fee', 'total_fee', 'time', 'coures_name', 'student_name', 'semester_name']

    def get_coures_name(self, obj):
        return ", ".join([course.course_title for course in obj.courses.all()])

    def get_student_name(self, obj):
        user = obj.student.user
        return f"{user.first_name} {user.last_name}"

    def get_semester_name(self, obj):
        return f"{obj.semester.name} {obj.semester.year}"

class ResultSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    batch_name = serializers.SerializerMethodField()
    semester_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = [
            'id', 'subject', 'batch', 'marks', 'exam_type', 'teacher', 'student', 'semester',
            'teacher_name', 'subject_name', 'batch_name', 'semester_name', 'student_name'
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.name if obj.teacher else None

    def get_subject_name(self, obj):
        return obj.subject.course_title if obj.subject else None

    def get_batch_name(self, obj):
        return obj.batch.name if obj.batch else None

    def get_semester_name(self, obj):
        return obj.semester.name+' '+str(obj.semester.year) if obj.semester else None

    def get_student_name(self, obj):
        return obj.student.user.first_name + ' ' + obj.student.user.last_name if obj.student else None

class AnnouncementSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.name', read_only=True)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'batch', 'batch_name', 'file']

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(required=True)
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    


    
