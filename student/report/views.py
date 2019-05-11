from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from student.account.models import User
from student.account.permissions import IsStaff
from student.course.models import CourseGroups
from student.daily_study.models import  Study


class UserReport(ViewSet):
    @action(detail=False, permission_classes=[IsAuthenticated, IsStaff])
    def total_student(self, request):
        user = request.user
        body = {}

        if user.is_teacher():
            body['total_student'] = User.objects.filter(user_type=User.STUDENT, classroom__teachers=user).count()
        elif user.is_executive():
            body['total_student'] = User.objects.filter(user_type=User.STUDENT,
                                                        classroom__area__executives=user).count()
            body['total_teacher'] = User.objects.filter(user_type=User.TEACHER,
                                                        classroom_teacher__area__executives=user).count()
        elif user.is_admin():
            body['total_student'] = User.objects.filter(user_type=User.STUDENT,
                                                        classroom__area__region__admins=user).count()

        return Response(body)


class DailyStudyReport(ViewSet):
    @action(detail=False, permission_classes=[IsAuthenticated, IsStaff])
    def admin(self, request):
        group = request.query_params.get('group', None)
        begining = request.query_params.get('begining', None)
        end = request.query_params.get('end', None)
        is_validated = request.query_params.get('is_validated', None)

        if group is None or begining is None or end is None or is_validated is None:
            return Response('query paramtrelerden biri eksik.', status=status.HTTP_400_BAD_REQUEST)

        staff = request.user

        region = 1
        area = request.query_params.get('area', None)
        classroom = request.query_params.get('classroom', None)
        # if staff.is_teacher() and classroom is None:
        #    return Response('Classroom seçilmedi?', status=status.HTTP_400_BAD_REQUEST)
        try:
            # if not Region.objects.filter(admins=staff, id=region).exists():
            #    return Response("region admini değilsin!? ", status=status.HTTP_403_FORBIDDEN)
            group = CourseGroups.objects.get(id=group)
            students = User.objects.filter(course_group=group, user_type=User.STUDENT) \
                .prefetch_related('dailystudy_set')

            # for student in students:
            #     ds = student.dailystudy_set.filter(created_day__gte=begining, created_day__lte=end)
            #     study = Study.objects.filter(daily_study__in=ds).aggregate(Sum('amount'))
            toplamlar = []
            for student in students:
                student_studies = {
                    'Name': str(student.first_name) + ' ' + str(student.last_name),
                    'Classroom': str(student.classroom.name)
                }

                ds = student.dailystudy_set.filter(created_day__gte=begining, created_day__lte=end)
                study = Study.objects.filter(daily_study__in=ds).values('course__name').annotate(Sum('amount'))

                for s in study:
                    student_studies[s['course__name']] = s['amount__sum']

                toplamlar.append(student_studies)

            return Response(toplamlar)
        except:
            return Response('invalid region or group or begining or end', status=status.HTTP_400_BAD_REQUEST)
