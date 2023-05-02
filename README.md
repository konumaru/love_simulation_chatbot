# gpt_love

<img src="./docs/img/demo.png" width=360>

## Commands

```sh
.venv ❯ make help
deploy: Deploy the Linebot app on google cloud run.
help: Show help for each of the Makefile recipes.
init: Initialize the project of gcp.
```

## Usage

```sh
# Set enviroment variables
cp .envrc.template .envrc

# Generate Charactors
python src/generate_charactors.py

# Upload Prompt
python src/upload_prompts.py

# Deploy bot to cloud function
cd functions/linebot
make deploy
```
