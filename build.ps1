rm -r dist
rm -r build
pipenv run pyinstaller --paths $(pipenv --venv) --add-binary "vendor/*;." --add-data "Rosmarus_test_data;Rosmarus_test_data" --hidden-import='pkg_resources.py2_warn' --clean --onefile --no-console .\functionality.py