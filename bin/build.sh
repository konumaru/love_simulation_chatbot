poetry export --without-hashes --format=requirements.txt > requirements.txt

docker build -t gpt-love .
