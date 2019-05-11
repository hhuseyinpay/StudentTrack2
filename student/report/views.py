from datetime import timedelta

from django.db.models import Sum, Q, Count, F
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from student.account.models import User
from student.account.permissions import IsStaff, IsAdmin
from student.course.models import CourseGroups
from student.daily_study.models import DailyStudy, Study
from student.location.models import Region, Area
from student.location.models import ClassRoom


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
        #    return Response('Medrese seçilmedi?', status=status.HTTP_400_BAD_REQUEST)
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


class Dashboard(ViewSet):
    @action(detail=False, permission_classes=[IsAuthenticated, IsStaff])
    def admin(self, request):
        staff = request.user
        body = {}

        students = User.objects.filter(user_type=User.STUDENT)
        teachers = User.objects.filter(user_type=User.TEACHER)
        executives = User.objects.filter(user_type=User.EXECUTIVE)

        classrooms = ClassRoom.objects.all()
        areas = Area.objects.all()
        daily_studies = DailyStudy.objects.all()

        # dünden itibaren 1 hafta
        bu_hafta_ds = daily_studies.filter(created_day__gte=(now().date() - timedelta(days=7)),
                                           created_day__lte=(now().date() - timedelta(days=1)))
        studies = Study.objects.all()

        if staff.is_teacher():
            body['ToplamTalebe'] = students.filter(classroom__teachers=staff).count()
            body['ToplamMedrese'] = classrooms.filter(teachers=staff).count()
            student_filter = (Q(user__classroom__teachers=staff))

        elif staff.is_executive():
            body['ToplamTalebe'] = students.filter(classroom__area__executives=staff).count()
            body['ToplamKatVakfi'] = teachers.filter(classroom_teacher__area__executives=staff).count()

            body['ToplamMedrese'] = classrooms.filter(area__executives=staff).count()
            body['ToplamIlce'] = areas.filter(executives=staff).count()
            student_filter = (Q(user__classroom__area__executives=staff))

        elif staff.is_admin():
            body['ToplamTalebe'] = students.filter(classroom__area__region__admins=staff).count()
            body['ToplamKatVakfi'] = teachers.filter(classroom_teacher__area__region__admins=staff).count()
            body['ToplamIlceVakfi'] = executives.filter(area_executive__region__admins=staff).count()

            body['ToplamMedrese'] = classrooms.filter(area__region__admins=staff).count()
            body['ToplamIlce'] = areas.filter(region__admins=staff).count()

            student_filter = (Q(user__classroom__area__region__admins=staff))
            # | Q(user__classroom_teacher__area__region__admins=staff) |
            # Q(user__area_executive__region__admins=staff))

        for tamamlanan in range(1, 8):
            bu_hafta_full_ds = bu_hafta_ds.values('user') \
                .filter(is_validated=True) \
                .annotate(tamamlanan=Count('updated')) \
                .filter(tamamlanan=tamamlanan)

            body['BuHafta' + str(tamamlanan) + 'gunCeteleDolduranlar'] = bu_hafta_full_ds.filter(student_filter).count()

        admin_bu_hafta_study = studies.filter(
            daily_study__in=bu_hafta_ds.filter(is_validated=True).filter(student_filter)
        )
        toplam_study = admin_bu_hafta_study.order_by('daily_study__created_day') \
            .annotate(tarih=F('daily_study__created_day')) \
            .values('tarih') \
            .annotate(toplam=Sum('amount'))

        body['BuHaftaKuran'] = toplam_study.filter(course=1)
        body['BuHaftaMutalaa'] = toplam_study.filter(course=2)
        body['BuHaftaEzber'] = toplam_study.filter(course=3)
        body['BuHaftaYazi'] = toplam_study.filter(course=4)
        body['BuHaftaCevsen'] = toplam_study.filter(course=5)

        return Response(body)
