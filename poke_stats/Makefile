conda-update:
	conda env update --prune -f environment.yml

pip-tools:
	python -m pip install pip-tools
	pip-compile requirements/base.in

# execute after pull this repo
	pip-sync requirements/base.txt

run:
	python .

watch:
	uvicorn app.app:app --reload

seed:
	python -m app.seeder.seeder
	