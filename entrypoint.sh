echo "ENVIRONMENT: ${ENVIRONMENT}"
exec ~/.local/share/virtualenvs/${PIPENV_CUSTOM_VENV_NAME}/bin/uvicorn "main:app" --host "0.0.0.0" --port 5000