from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import TaskSerializer
from .models import Task
from django.contrib.auth.models import User
import re
from .permissions import IsTeamMember
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    request=TaskSerializer,
    responses={201: TaskSerializer},
    summary="ایجاد تسک جدید",
    description=(
        "کاربران عضو تیم می‌توانند تسک جدید بسازند.\n"
        "در توضیحات (description) اگر از علامت @username استفاده شود، آن کاربران به عنوان tagged_users اضافه می‌شوند."
    ),
    tags=['Tasks'],
    examples=[
        OpenApiExample(
            name="نمونه درخواست ایجاد تسک",
            value={
                "title": "بررسی باگ‌های نسخه جدید",
                "description": "لطفاً تست کن @sara و @ali",
                "due_date": "2025-11-04T06:00:00+03:30",
                "priority": "high",
                "assignee": 2,
                "team": 1
            },
            request_only=True,
        ),
        OpenApiExample(
            name="نمونه پاسخ ایجاد تسک",
            value={
                "id": 5,
                "title": "بررسی باگ‌های نسخه جدید",
                "description": "لطفاً تست کن @sara و @ali",
                "due_date": "2025-11-04T06:00:00+03:30",
                "priority": "high",
                "creator_info": {"id": 1, "username": "arash"},
                "assignee_info": {"id": 2, "username": "sara"},
                "tagged_users_info": [
                    {"id": 2, "username": "sara"},
                    {"id": 3, "username": "ali"}
                ],
                "team": 1
            },
            response_only=True,
        ),
    ]
)


class TaskCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeamMember]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(creator=request.user)

        # استخراج @mention ها
        mentions = re.findall(r'@(\w+)', task.description)
        tagged_users = []
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                tagged_users.append(user)
            except User.DoesNotExist:
                continue
        if tagged_users:
            task.tagged_users.add(*tagged_users)
            # TODO: ارسال نوتیفیکیشن بلادرنگ

        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={200: TaskSerializer(many=True)},
    summary="دریافت لیست تسک‌های تیم‌های کاربر",
    description="تمام تسک‌هایی که کاربر عضو تیم آن‌هاست، در این endpoint برگردانده می‌شود.",
    tags=['Tasks'],
    examples=[
        OpenApiExample(
            "نمونه پاسخ لیست تسک‌ها",
            value=[
                {
                    "id": 1,
                    "title": "رفع باگ لاگین",
                    "description": "بررسی کن @mohammad",
                    "due_date": "2025-11-05T09:00:00+03:30",
                    "priority": "medium",
                    "creator_info": {"id": 1, "username": "arash"},
                    "assignee_info": {"id": 2, "username": "mohammad"},
                    "tagged_users_info": [{"id": 2, "username": "mohammad"}],
                    "team": 1
                }
            ],
            response_only=True
        )
    ]
)


class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(team__members=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


@extend_schema(
    responses={200: TaskSerializer},
    summary="نمایش جزئیات یک تسک",
    description="فقط اعضای تیم می‌توانند جزئیات تسک را ببینند.",
    tags=['Tasks'],
    examples=[
        OpenApiExample(
            "نمونه پاسخ جزئیات تسک",
            value={
                "id": 1,
                "title": "رفع باگ لاگین",
                "description": "بررسی کن @mohammad",
                "due_date": "2025-11-05T09:00:00+03:30",
                "priority": "medium",
                "creator_info": {"id": 1, "username": "arash"},
                "assignee_info": {"id": 2, "username": "mohammad"},
                "tagged_users_info": [{"id": 2, "username": "mohammad"}],
                "team": 1
            },
            response_only=True
        )
    ]
)


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeamMember]

    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task)
        return Response(serializer.data)
