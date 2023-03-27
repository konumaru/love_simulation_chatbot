#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
SA_NAME=linebot-identity 


# Create service account.
gcloud iam service-accounts create ${SA_NAME} --display-name="linebot"


# Grant the necessary authorization.
roles=(
    "roles/viewer"
    "roles/storage.admin"
    "roles/run.invoker"
    "roles/artifactregistry.writer"
)

for role in "${roles[@]}" ; do 
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member "serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role "${role}"
done

