FROM openenv-base:latest
WORKDIR /app
COPY server/ ./server/
COPY models.py reward.py ./
COPY students/ ./students/
COPY pyproject.toml ./
RUN pip install openenv-core fastapi uvicorn
# DO NOT install anthropic — simulator is local
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
