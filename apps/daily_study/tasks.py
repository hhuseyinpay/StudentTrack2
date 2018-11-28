from datetime import timedelta

from django.utils.timezone import now
from celery import shared_task

from account.models import User
from .models import DailyStudy, Study


@shared_task
def fill_missing_daily_study():
    yesterday = (now() - timedelta(days=1)).date()
    students = User.objects \
        .filter(user_type=User.STUDENT) \
        .exclude(dailystudy__created_day=yesterday).only('id', 'course_group') \
        .prefetch_related('course_group__courses')

    for u in students:
        ds = DailyStudy.objects.create(user=u, created_day=yesterday)

        studies = []
        for course in u.course_group.courses.all():
            studies.append(Study(daily_study=ds, course=course, begining=0, end=0, amount=0))
        Study.objects.bulk_create(studies)
    return True
