#!/bin/bash

# Start the FastAPI application using uvicorn
cd /srv/text_to_image && uvicorn app:app --reload --workers 1 --host 0.0.0.0 --port 8000
