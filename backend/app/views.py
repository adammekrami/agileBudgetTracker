from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Project, Sprint, SprintMetric
from .serializers import (
    UserSerializer,
    ProjectSerializer,
    SprintSerializer,
    SprintMetricSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project model.
    Provides full CRUD operations for projects.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def sprints(self, request, pk=None):
        """
        Custom action to get all sprints for a specific project.
        URL: /api/projects/{id}/sprints/
        """
        project = self.get_object()
        sprints = project.sprints.all()
        serializer = SprintSerializer(sprints, many=True)
        return Response(serializer.data)


class SprintViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Sprint model.
    Provides full CRUD operations for sprints.
    """
    queryset = Sprint.objects.select_related('project', 'metrics').all()
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']


class SprintMetricViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SprintMetric model.
    Provides full CRUD operations for sprint metrics.
    Automatically calculates and returns ROI.
    """
    queryset = SprintMetric.objects.select_related('sprint', 'sprint__project').all()
    serializer_class = SprintMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['cost', 'estimated_business_value', 'velocity']
    
    @action(detail=False, methods=['get'])
    def high_roi(self, request):
        """
        Custom action to get sprints with ROI > 0.5 (50%).
        URL: /api/sprint-metrics/high_roi/
        """
        high_roi_metrics = [
            metric for metric in self.get_queryset()
            if metric.roi is not None and metric.roi > 0.5
        ]
        serializer = self.get_serializer(high_roi_metrics, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for User model.
    Read-only to prevent unauthorized user modifications via API.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['role']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']