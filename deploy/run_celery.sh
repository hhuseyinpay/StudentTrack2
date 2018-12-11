#!/usr/bin/env bash

# multi start w1
celery  -A student.settings.celery:app worker -l INFO --pidfile="/tmp/celery%n.pid" &
celery  -A student.settings.celery:app beat -l INFO --scheduler=django_celery_beat.schedulers:DatabaseScheduler --pidfile="/tmp/beat%n.pid" &
celery flower -A student.settings.celery:app --broker=redis://redis:6379/ -l INFO --pidfile="/tmp/flower.pid"
