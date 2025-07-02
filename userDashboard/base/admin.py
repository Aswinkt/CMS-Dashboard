from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Complaints, UserLoginSession, EmployeeCheckIn

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'full_name', 'is_employee', 'is_superuser', 'is_active', 'date_joined')
    list_filter = ('is_employee', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'full_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_employee', 'full_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('is_employee', 'full_name')}),
    )

@admin.register(Complaints)
class ComplaintsAdmin(admin.ModelAdmin):
    list_display = ('title', 'complainant_name', 'assignee', 'status', 'created_date', 'modified_date')
    list_filter = ('status', 'created_date', 'assignee')
    search_fields = ('title', 'complaint', 'complainant_name', 'assignee__username')
    ordering = ('-created_date',)
    readonly_fields = ('object_id', 'created_date', 'modified_date')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'complaint', 'object_id')
        }),
        ('Assignment & Status', {
            'fields': ('assignee', 'status', 'comments')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'modified_date'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserLoginSession)
class UserLoginSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_datetime', 'ip_address', 'location', 'is_active')
    list_filter = ('is_active', 'login_datetime', 'user')
    search_fields = ('user__username', 'ip_address', 'location')
    ordering = ('-login_datetime',)
    readonly_fields = ('login_datetime',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_active')
        }),
        ('Login Details', {
            'fields': ('login_datetime', 'logout_datetime')
        }),
        ('Location Information', {
            'fields': ('ip_address', 'location', 'city', 'country')
        }),
        ('Technical Details', {
            'fields': ('user_agent',),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmployeeCheckIn)
class EmployeeCheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'checkin_datetime', 'checkout_datetime', 'checkin_location', 'is_active', 'duration_display')
    list_filter = ('is_active', 'checkin_datetime', 'user')
    search_fields = ('user__username', 'user__full_name', 'checkin_location')
    ordering = ('-checkin_datetime',)
    readonly_fields = ('checkin_datetime', 'duration_display')
    
    def duration_display(self, obj):
        if obj.duration:
            hours = obj.duration.seconds // 3600
            minutes = (obj.duration.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "Active"
    duration_display.short_description = 'Duration'
