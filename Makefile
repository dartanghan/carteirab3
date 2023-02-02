setup: requirements.txt
	python3 -m venv venv && 

format:
	autopep8 --in-place --recursive .

run: setup format
	uvicorn main:app --port 5000