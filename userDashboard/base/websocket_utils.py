from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def send_dashboard_update():
    """Send dashboard update to all connected clients"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "dashboard_updates",
        {
            "type": "dashboard_update",
            "message": "Dashboard data updated"
        }
    )

def send_complaint_update(complaint_id, action="updated"):
    """Send complaint update notification"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "complaint_updates",
        {
            "type": "complaint_update",
            "complaint_id": complaint_id,
            "action": action,
            "message": f"Complaint {action}"
        }
    )

def send_new_complaint_notification(complaint_data):
    """Send new complaint notification"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "complaint_updates",
        {
            "type": "new_complaint",
            "complaint": complaint_data,
            "message": "New complaint created"
        }
    )

def send_user_notification(user_id, message, notification_type="info"):
    """Send notification to specific user"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}_notifications",
        {
            "type": "notification",
            "message": message,
            "notification_type": notification_type
        }
    )

def send_admin_notification(message, notification_type="info"):
    """Send notification to all admin users"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "dashboard_updates",
        {
            "type": "notification",
            "message": message,
            "notification_type": notification_type,
            "target": "admin"
        }
    ) 