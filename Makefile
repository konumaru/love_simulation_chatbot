.PHONY: run
run:
	uvicorn app.main:app --reload --host=0.0.0.0
