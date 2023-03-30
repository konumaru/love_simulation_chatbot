#!/bin/bash

PROJECT_ID=$(gcloud config get-value project)
IMAGE_NAME='linebot'
VERSION='v2'

docker build -t gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION} .
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION}

gcloud run deploy ${IMAGE_NAME} \
    --image gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION} \
    --service-account ${IMAGE_NAME}-identity \
    --platform managed \
    --set-env-vars "LINEAPI_ACCESS_TOKEN=${LINEAPI_ACCESS_TOKEN}" \
    --set-env-vars "LINEAPI_CHANNEL_SECRET=${LINEAPI_CHANNEL_SECRET}" \
    --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY}" \
    --region us-east1 \
    --allow-unauthenticated
