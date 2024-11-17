ARG PYTHON_VERSION=3.10.6
FROM python:${PYTHON_VERSION}-slim

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Tell pipenv to create venv in custom directory
ENV PIPENV_CUSTOM_VENV_NAME=battleship_venv

# Download dependencies as a separate step to take advantage of Docker's caching.
RUN apt-get update

# Copy the source code into the container.
COPY Pipfile ./

RUN pip install -U pipenv

RUN pipenv install --dev

COPY . .

# Expose the port that the application listens on.
EXPOSE 5000

# Run the application.
ENTRYPOINT ["sh", "entrypoint.sh"]