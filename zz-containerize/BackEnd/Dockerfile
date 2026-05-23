#using node verison 22 that we uses in our frontend
#-slim is to help docker able to download stuff from requirement file
FROM python:3.10.19-slim

WORKDIR /.

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#copy everything in the app into container

COPY requirements.txt .
# RUN pip install requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "webAPI:app", "--host", "0.0.0.0", "--port", "8000"]
