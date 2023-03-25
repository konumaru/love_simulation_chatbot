aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 133956609744.dkr.ecr.ap-southeast-2.amazonaws.com
docker build -t gpt-love .
docker tag gpt-love:latest 133956609744.dkr.ecr.ap-southeast-2.amazonaws.com/gpt-love:latest
docker push 133956609744.dkr.ecr.ap-southeast-2.amazonaws.com/gpt-love:latest
