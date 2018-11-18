FROM python:3.7

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/student/src

WORKDIR /opt/services/student/src
COPY . /opt/services/student/src


RUN pip install -r requirements.txt

RUN python manage.py collectstatic --no-input

EXPOSE 8000
CMD ["gunicorn", "-c", "deploy/config/gunicorn-conf.py", "--bind", ":8000", "--chdir", "student", "student.wsgi:application"]