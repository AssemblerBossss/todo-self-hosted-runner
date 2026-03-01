#!/bin/bash

sleep 10

alembic upgrade head

uvicorn app.main:app --reload --host 0.0.0.0