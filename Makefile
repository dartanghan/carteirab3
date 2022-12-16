setup: requirements.txt
	python3 -m venv venv
	pip3 install -r requirements.txt

format:
	autopep8 --in-place --recursive .

run: setup format
	uvicorn main:app --port 5000