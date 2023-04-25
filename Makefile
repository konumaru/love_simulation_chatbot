default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done


.PHONY: init
init: # Initialize the project of gcp.
	./bin/init_gcp.sh


.PHONY: deploy
deploy: # Deploy the Linebot app on google cloud run.
	./bin/deploy.sh


.PHONY: ngrok
run-local: # Run the Linebot app on local for testing.
	ngrok http 8080


.PHONY: run
run:
	python app/main.py
