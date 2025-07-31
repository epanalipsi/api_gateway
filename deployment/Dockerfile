FROM continuumio/miniconda3

ARG WORK_DIR=/ml_api

COPY ./ $WORK_DIR
WORKDIR $WORK_DIR

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install -y poppler-utils -y
RUN pip install -r requirements.txt

EXPOSE $PORT
ENTRYPOINT ["uvicorn", "app:app", "--port=10000", "--host=0.0.0.0"]
# ENTRYPOINT ["./entrypoint.sh"]