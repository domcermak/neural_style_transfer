.PHONY: run install run_presentation_app run_upload_app run_neural_worker serve

run :
	docker-compose up

install :
	mkdir -p data/out
	chmod o+w data/out
	python3 setup.py install

run_presentation_app :
	streamlit run presentation_app/__init__.py --server.port 8051

run_upload_app :
	streamlit run upload_app/__init__.py --server.port 8080

run_neural_worker :
	python3 neural_worker/__init__.py

serve :
	ngrok http 8080