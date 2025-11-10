from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Agile Budget Tracker API",
        default_version='v1',
        description="""
        API for managing Agile projects, sprints, and financial metrics.
        
        Key Features:
        - Project management
        - Sprint tracking
        - Automatic ROI calculation
        - Financial metrics
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@agiletracker.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('app.urls')),
    
    # Django REST Framework browsable API authentication
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    
    # ReDoc UI (alternative to Swagger)
    path('redoc/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
]