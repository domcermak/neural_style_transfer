build :
	python src/setup.py build

install :
	python src/setup.py install

run :
	streamlit run src/neural_style_transfer/__init__.py