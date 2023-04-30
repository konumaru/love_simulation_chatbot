REGION = asia-northeast1
FUNCTION_NAME = linebot
ENTORY_POINT = main

default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done


.PHONY: deploy 
deploy: # Deploy the Linebot app on google cloud run.
	cp -r ../../src/utils ./	
	poetry run pip freeze > requirements.txt
	gcloud functions deploy $(FUNCTION_NAME) \
		--gen2 \
		--runtime=python311 \
		--region $(REGION) \
		--source=. \
		--entry-point $(ENTORY_POINT) \
		--trigger-http \
		--timeout=600 \
		--set-env-vars "LINEAPI_ACCESS_TOKEN=${LINEAPI_ACCESS_TOKEN}" \
		--set-env-vars "LINEAPI_CHANNEL_SECRET=${LINEAPI_CHANNEL_SECRET}" \
		--set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY}" \
		--set-env-vars "GCS_BUCKET_NAME=${GCS_BUCKET_NAME}" \
		--ignore-file=.gcloudignore \
		--allow-unauthenticated
	rm requirements.txt

.PHONY: delete
delete: # Delete the Linebot app on google cloud run.
	gcloud functions delete $(FUNCTION_NAME) \
		--region $(REGION) \
		--gen2

.PHONY: tests
tests:
	poetry run pytest
