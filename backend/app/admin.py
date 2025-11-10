from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, Sprint, SprintMetric


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for custom User model.
    Extends Django's built-in UserAdmin to include the 'role' field.
    """
    # Fields to display in the user list
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # Add 'role' to the user edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )
    
    # Add 'role' to the user creation form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for Project model.
    """
    list_display = ['name', 'created_at', 'sprint_count']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    def sprint_count(self, obj):
        """Display the number of sprints for each project."""
        return obj.sprints.count()
    sprint_count.short_description = 'Number of Sprints'


class SprintMetricInline(admin.StackedInline):
    """
    Inline admin for SprintMetric.
    Allows editing metrics directly within the Sprint admin page.
    """
    model = SprintMetric
    extra = 0  # Don't show extra empty forms
    fields = ['cost', 'estimated_business_value', 'velocity', 'display_roi']
    readonly_fields = ['display_roi']
    
    def display_roi(self, obj):
        """Display calculated ROI in the admin."""
        if obj.roi is None:
            return "N/A (cost is zero)"
        return f"{obj.roi:.2%}"
    display_roi.short_description = 'ROI'


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    """
    Admin interface for Sprint model.
    Includes inline editing of sprint metrics.
    """
    list_display = ['__str__', 'project', 'start_date', 'end_date', 'created_at', 'has_metrics']
    list_filter = ['project', 'start_date', 'end_date']
    search_fields = ['project__name']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at']
    inlines = [SprintMetricInline]
    
    # Group fields in the form
    fieldsets = (
        ('Sprint Information', {
            'fields': ('project', 'start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
    
    def has_metrics(self, obj):
        """Show whether this sprint has metrics defined."""
        try:
            return obj.metrics is not None
        except SprintMetric.DoesNotExist:
            return False
    has_metrics.boolean = True  # Display as a green checkmark or red X
    has_metrics.short_description = 'Has Metrics'


@admin.register(SprintMetric)
class SprintMetricAdmin(admin.ModelAdmin):
    """
    Admin interface for SprintMetric model.
    Displays calculated ROI.
    """
    list_display = ['sprint', 'cost', 'estimated_business_value', 'velocity', 'display_roi']
    list_filter = ['sprint__project']
    search_fields = ['sprint__project__name']
    readonly_fields = ['display_roi']
    
    # Group fields in the form
    fieldsets = (
        ('Sprint', {
            'fields': ('sprint',)
        }),
        ('Financial Metrics', {
            'fields': ('cost', 'estimated_business_value')
        }),
        ('Performance Metrics', {
            'fields': ('velocity',)
        }),
        ('Calculated Values', {
            'fields': ('display_roi',),
            'classes': ('collapse',)
        }),
    )
    
    def display_roi(self, obj):
        """Display calculated ROI as a formatted percentage."""
        if obj.roi is None:
            return "N/A (cost is zero)"
        
        # Color-code the ROI based on performance
        roi_percent = obj.roi * 100
        if roi_percent > 50:
            color = 'green'
        elif roi_percent > 0:
            color = 'orange'
        else:
            color = 'red'
        
        return f'<span style="color: {color}; font-weight: bold;">{obj.roi:.2%}</span>'
    
    display_roi.short_description = 'ROI'
    display_roi.allow_tags = True  # Allow HTML in the display