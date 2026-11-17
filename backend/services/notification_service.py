import uuid
import datetime
from backend.services.supabase_service import supabase_service

class NotificationService:
    """
    Automated Farmer Notification & Alert Service
    """
    def create_notification(self, user_id: str, title: str, message: str, notification_type: str = "General", scheduled_at: str = None):
        if not user_id:
            return None
            
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "is_read": False,
            "scheduled_at": scheduled_at or datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        if supabase_service.is_configured and supabase_service.client:
            try:
                supabase_service.client.table("notifications").insert(record).execute()
            except Exception as e:
                print(f"[NotificationService] Insert error: {e}")
                
        return record

    def get_user_notifications(self, user_id: str, unread_only: bool = False):
        if not user_id:
            return []
            
        if supabase_service.is_configured and supabase_service.client:
            try:
                query = supabase_service.client.table("notifications").select("*").eq("user_id", user_id)
                if unread_only:
                    query = query.eq("is_read", False)
                res = query.order("created_at", desc=True).limit(20).execute()
                return res.data
            except Exception as e:
                print(f"[NotificationService] Fetch error: {e}")
                
        return [
            {
                "id": "sample-notif-1",
                "title": "Irrigation Reminder",
                "message": "Wheat is entering Crown Root Initiation stage. 1st irrigation recommended within 48 hours.",
                "notification_type": "Irrigation",
                "is_read": False,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
        ]

    def mark_as_read(self, notification_id: str):
        if supabase_service.is_configured and supabase_service.client:
            try:
                supabase_service.client.table("notifications").update({"is_read": True}).eq("id", notification_id).execute()
                return True
            except Exception as e:
                print(f"[NotificationService] Update error: {e}")
        return True

# Global singleton
notification_service = NotificationService()
