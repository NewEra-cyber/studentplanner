from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import UserTimetable, JKUATTimetable, SmartActivity
from core.smart_scheduler import SmartScheduler

@receiver(post_save, sender=UserTimetable)
def adjust_schedule_on_timetable_save(sender, instance, created, **kwargs):
    """Auto-adjust smart activities when timetable is saved"""
    if instance.is_active:
        scheduler = SmartScheduler(instance.user)
        scheduler.adjust_schedule_for_timetable(instance.day)

@receiver(post_delete, sender=UserTimetable)
def adjust_schedule_on_timetable_delete(sender, instance, **kwargs):
    """Auto-adjust smart activities when timetable is deleted"""
    scheduler = SmartScheduler(instance.user)
    scheduler.adjust_schedule_for_timetable(instance.day)

@receiver(post_save, sender=JKUATTimetable)
def adjust_schedule_on_jkuat_save(sender, instance, created, **kwargs):
    """Auto-adjust smart activities when JKUAT timetable is saved"""
    if instance.is_active:
        scheduler = SmartScheduler(instance.user)
        scheduler.adjust_schedule_for_timetable(instance.day)

@receiver(post_delete, sender=JKUATTimetable)
def adjust_schedule_on_jkuat_delete(sender, instance, **kwargs):
    """Auto-adjust smart activities when JKUAT timetable is deleted"""
    scheduler = SmartScheduler(instance.user)
    scheduler.adjust_schedule_for_timetable(instance.day)