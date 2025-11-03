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


class TaskAssignView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeamMember]

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        # بررسی اینکه درخواست‌دهنده عضو تیم است
        self.check_object_permissions(request, task)

        assignee_id = request.data.get("assignee_id")
        if not assignee_id:
            return Response({"detail": "assignee_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignee = User.objects.get(id=assignee_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # بررسی اینکه assignee عضو همان تیم است
        if assignee not in task.team.members.all():
            return Response({"detail": "User is not a member of this team."}, status=status.HTTP_403_FORBIDDEN)

        # تخصیص وظیفه
        task.assignee = assignee
        task.save()

        # TODO: ارسال نوتیفیکیشن بلادرنگ
        message = f"وظیفه '{task.title}' به شما واگذار شد."

        return Response({
            "message": "Task assigned successfully.",
            "assigned_to": {"id": assignee.id, "username": assignee.username},
            "task": task.title
        }, status=status.HTTP_200_OK)