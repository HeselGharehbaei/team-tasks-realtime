# notifications/tasks.py

from celery import shared_task
from datetime import datetime
from django.contrib.auth.models import User
from tasks.models import Task
from .utils import send_realtime_notification
from django.utils import timezone


@shared_task
def send_task_notification(user_id, type_, title, message, task_id=None):
    """
    ارسال نوتیفیکیشن بلادرنگ به کاربر.
    نوع: assignment | mention | overdue
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    task = None
    if task_id:
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            pass

    send_realtime_notification(
        user=user,
        type_=type_,
        title=title,
        message=message,
        task=task
    )



DEFAULT_USER_ID = 1  # ID کاربر anonymous یا پیش‌فرض

@shared_task
def check_overdue_tasks():
    now = timezone.now()
    print(f"[CELERY] Current datetime (aware): {now} ({type(now)})")

    overdue_tasks = Task.objects.all()
    for task in overdue_tasks:
        due_date = task.due_date
        print(f"[CELERY] Task '{task.title}' due_date: {due_date} ({type(due_date)})")

        # مطمئن شدن که due_date timezone-aware است
        if timezone.is_naive(due_date):
            due_date = timezone.make_aware(due_date, timezone=timezone.get_default_timezone())

        if due_date < now:
            # اگر assignee ندارد، کاربر پیش‌فرض را استفاده کن
            user = task.assignee if task.assignee else User.objects.get(id=DEFAULT_USER_ID)

            send_task_notification.delay(
                user_id=user.id,
                type_='overdue',
                title='وظیفه دیرکرده',
                message=f"وظیفه '{task.title}' به موعد خودش رسیده است.",
                task_id=task.id
            )
            print(f"[CELERY] Task '{task.title}' is overdue! Notification sent to user ID: {user.id}")