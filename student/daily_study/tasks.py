from __future__ import absolute_import, unicode_literals

from django.utils.timezone import now

from celery import shared_task
from student.account.models import User
from .models import DailyStudy, Study


@shared_task
def fill_today_daily_study():
    today = now().date()
    try:
        students = User.objects \
            .exclude(course_group__isnull=True) \
            .only('id', 'course_group') \
            .prefetch_related('course_group__courses')

        for student in students:
            if DailyStudy.objects.filter(user=student, created_day=today).exists():
                continue

            ds = DailyStudy.objects.create(user=student, created_day=today)
            studies = []
            for course in student.course_group.courses.all():
                studies.append(Study(daily_study=ds, course=course, begining=0, end=0, amount=0))
            Study.objects.bulk_create(studies)
    except Exception as e:
        return repr(e)
    return True
