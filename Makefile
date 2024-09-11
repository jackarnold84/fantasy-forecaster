EVENT=model/events/test.json

default: sam

sam:
	sam build

invoke: sam
	sam local invoke FantasyForecasterModel --event $(EVENT)

serve-local: sam
	sam local start-lambda

deploy: sam
	sam deploy --guided
