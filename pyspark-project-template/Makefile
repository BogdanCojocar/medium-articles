.DEFAULT_GOAL := run

init:
	pipenv --three install
	pipenv shell

analyze:
	flake8 ./src

run_tests:
	pytest --cov=src test/jobs/

# comand line example: make run JOB_NAME=pi CONF_PATH=/your/path/pyspark-project-template/src/jobs
run:
	# cleanup
	find . -name '__pycache__' | xargs rm -rf
	rm -f jobs.zip

	# create the zip
	cd src/ && zip -r ../jobs.zip jobs/

  # run the job
	spark-submit --py-files jobs.zip src/main.py --job $(JOB_NAME) --res-path $(CONF_PATH)
