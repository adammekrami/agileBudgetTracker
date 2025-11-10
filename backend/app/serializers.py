from rest_framework import serializers
from .models import User, Project, Sprint, SprintMetric


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Excludes password for security (use separate serializer for user creation).
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    Includes a count of associated sprints.
    """
    sprint_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'sprint_count']
        read_only_fields = ['id', 'created_at']
    
    def get_sprint_count(self, obj):
        """Return the number of sprints in this project."""
        return obj.sprints.count()


class SprintMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for SprintMetric model.
    Includes calculated ROI as a read-only field.
    """
    roi = serializers.SerializerMethodField()
    
    class Meta:
        model = SprintMetric
        fields = ['sprint', 'cost', 'estimated_business_value', 'velocity', 'roi']
        read_only_fields = ['roi']
    
    def get_roi(self, obj):
        """
        Calculate and return ROI.
        Handles zero cost gracefully by returning None.
        """
        if obj.cost == 0:
            return None
        
        roi_value = (obj.estimated_business_value - obj.cost) / obj.cost
        # Round to 4 decimal places for cleaner API response
        return round(float(roi_value), 4)


class SprintSerializer(serializers.ModelSerializer):
    """
    Serializer for Sprint model.
    Includes nested metrics if they exist.
    """
    metrics = SprintMetricSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Sprint
        fields = ['id', 'project', 'project_name', 'start_date', 'end_date', 'created_at', 'metrics']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """
        Validate that end_date is not before start_date.
        """
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after or equal to start date.'
                })
        return data