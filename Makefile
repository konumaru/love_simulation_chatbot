.PHONY: init
init:
	./bin/init_gcp.sh


.PHONY: deploy
deploy:
	./bin/deploy.sh


.PHONY: ngrok
ngrok:
	ngrok http 8080


.PHONY: run
run:
	uvicorn main:app --host 0.0.0.0 --port $PORT --reload
