from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SprintViewSet, SprintMetricViewSet, UserViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'sprints', SprintViewSet, basename='sprint')
router.register(r'sprint-metrics', SprintMetricViewSet, basename='sprintmetric')
router.register(r'users', UserViewSet, basename='user')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]