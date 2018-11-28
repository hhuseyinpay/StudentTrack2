#!/usr/bin/env bash

# multi start w1
celery multi start w1 -A student.settings.celery:app worker -l INFO --pidfile= &
celery multi start w1 -A student.settings.celery:app beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --pidfile= &
celery flower -A student.settings.celery:app --broker=redis://redis:6379/ -l INFO --pidfile=
