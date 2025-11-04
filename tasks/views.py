from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import TaskSerializer, TaskAssignResponseSerializer, TaskMentionRequestSerializer, TaskMentionResponseSerializer
from .models import Task
from django.contrib.auth.models import User
import re
from .permissions import IsTeamMember
from drf_spectacular.utils import extend_schema, OpenApiExample


class TaskCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeamMember]

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


class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]


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


    @extend_schema(
        summary="تخصیص وظیفه به یکی از اعضای تیم",
        description="فقط اعضای تیم می‌توانند وظیفه را به یکی از اعضای همان تیم واگذار کنند.",
        tags=['Tasks'],
        request=None,
        responses={200: TaskAssignResponseSerializer},
        examples=[
            OpenApiExample(
                "نمونه درخواست",
                value={"assignee_id": 3},
            ),
            OpenApiExample(
                "نمونه پاسخ موفق",
                value={
                    "message": "Task assigned successfully.",
                    "assigned_to": {"id": 3, "username": "sara"},
                    "task": "طراحی API لاگین"
                },
                response_only=True
            )
        ]
    )
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
    

class TaskMentionView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeamMember]

    @extend_schema(
        summary="تگ کردن کاربران در توضیحات وظیفه",
        description="کاربران می‌توانند در توضیح وظیفه سایر اعضای تیم را با @username تگ کنند. برای هر کاربر تگ‌شده، نوتیفیکیشن بلادرنگ ارسال خواهد شد.",
        tags=['Tasks'],
        request=TaskMentionRequestSerializer,
        responses={200: TaskMentionResponseSerializer},
        examples=[
            OpenApiExample(
                "نمونه درخواست",
                value={"description": "لطفاً بررسی کنید @ali @sara"},
                request_only=True
            ),
            OpenApiExample(
                "نمونه پاسخ موفق",
                value={
                    "message": "Users tagged successfully.",
                    "tagged_users": [
                        {"id": 2, "username": "ali"},
                        {"id": 3, "username": "sara"}
                    ]
                },
                response_only=True
            )
        ]
    )
    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, task)

        serializer = TaskMentionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        description = serializer.validated_data["description"]

        # پیدا کردن همه‌ی @usernameها
        mentioned_usernames = re.findall(r'@(\w+)', description)
        if not mentioned_usernames:
            return Response({"detail": "No usernames mentioned."}, status=status.HTTP_400_BAD_REQUEST)

        # پیدا کردن کاربران
        users = User.objects.filter(username__in=mentioned_usernames)
        team_members = task.team.members.all()

        # فقط اعضای تیم مجازند
        valid_users = [u for u in users if u in team_members]

        # افزودن به tagged_users
        task.tagged_users.add(*valid_users)
        task.description = description
        task.save()

        # TODO: ارسال نوتیفیکیشن بلادرنگ
        for user in valid_users:
            print(f"📢 {request.user.username} شما را در '{task.title}' تگ کرد")

        response_data = {
            "message": "Users tagged successfully.",
            "tagged_users": [{"id": u.id, "username": u.username} for u in valid_users]
        }
        return Response(response_data, status=status.HTTP_200_OK)
