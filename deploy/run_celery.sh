#!/usr/bin/env bash

rm ./*.pid

# multi start w1
celery multi start w2 -A student.settings.celery:app worker -l INFO --pidfile="./%n.pid" &
celery multi start w2 -A student.settings.celery:app beat -l INFO --scheduler=django_celery_beat.schedulers:DatabaseScheduler --pidfile="./%nB.pid" &
celery flower -A student.settings.celery:app --broker=redis://redis:6379/ -l INFO --pidfile="./%nF.pid"
