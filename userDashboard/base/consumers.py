import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Complaints, User, UserLoginSession
from django.db.models import Count

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        if self.scope["user"].is_authenticated:
            # Join the dashboard group
            await self.channel_layer.group_add(
                "dashboard_updates",
                self.channel_name
            )
            await self.accept()
            
            # Send initial dashboard data
            await self.send_dashboard_data()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave the dashboard group
        await self.channel_layer.group_discard(
            "dashboard_updates",
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle any messages from the client
        pass

    async def send_dashboard_data(self):
        """Send current dashboard statistics"""
        data = await self.get_dashboard_data()
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': data
        }))

    @database_sync_to_async
    def get_dashboard_data(self):
        """Get dashboard statistics"""
        user = self.scope["user"]
        
        if user.is_superuser:
            # Admin dashboard data
            total_employees = User.objects.filter(is_employee=True).count()
            total_complaints = Complaints.objects.count()
            pending_complaints = Complaints.objects.filter(status='Pending').count()
            in_progress_complaints = Complaints.objects.filter(status='In Progress').count()
            closed_complaints = Complaints.objects.filter(status='Closed').count()
            escalated_complaints = Complaints.objects.filter(status='Escalated').count()
            
            return {
                'type': 'admin_dashboard',
                'total_employees': total_employees,
                'total_complaints': total_complaints,
                'pending_complaints': pending_complaints,
                'in_progress_complaints': in_progress_complaints,
                'closed_complaints': closed_complaints,
                'escalated_complaints': escalated_complaints,
            }
        else:
            # Employee dashboard data
            assigned_complaints = Complaints.objects.filter(assignee=user).count()
            pending_assigned = Complaints.objects.filter(assignee=user, status='Pending').count()
            in_progress_assigned = Complaints.objects.filter(assignee=user, status='In Progress').count()
            closed_assigned = Complaints.objects.filter(assignee=user, status='Closed').count()
            
            return {
                'type': 'employee_dashboard',
                'assigned_complaints': assigned_complaints,
                'pending_assigned': pending_assigned,
                'in_progress_assigned': in_progress_assigned,
                'closed_assigned': closed_assigned,
            }

    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.send(text_data=json.dumps(event))

    async def complaint_update(self, event):
        """Send complaint update to WebSocket"""
        await self.send(text_data=json.dumps(event))

    async def notification(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps(event))


class ComplaintConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            # Join complaint-specific group
            await self.channel_layer.group_add(
                "complaint_updates",
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "complaint_updates",
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle complaint-related messages
        pass

    async def complaint_update(self, event):
        """Send complaint update to WebSocket"""
        await self.send(text_data=json.dumps(event))

    async def new_complaint(self, event):
        """Send new complaint notification"""
        await self.send(text_data=json.dumps(event))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            # Join user-specific notification group
            user_id = self.scope["user"].id
            await self.channel_layer.group_add(
                f"user_{user_id}_notifications",
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            user_id = self.scope["user"].id
            await self.channel_layer.group_discard(
                f"user_{user_id}_notifications",
                self.channel_name
            )

    async def receive(self, text_data):
        pass

    async def notification(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps(event)) 