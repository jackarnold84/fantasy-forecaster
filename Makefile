MODEL_EVENT=model/events/test.json
MODEL_ENV=model/events/environment.json
API_EVENT=api/events/test.json

default: sam

sam:
	sam build

invoke-model: sam
	sam local invoke FantasyForecasterModel --event $(MODEL_EVENT) --env-vars $(MODEL_ENV)

invoke-api: sam
	sam local invoke FantasyForecasterApi --event $(API_EVENT)

serve-local: sam
	sam local start-lambda

deploy: sam
	sam deploy
