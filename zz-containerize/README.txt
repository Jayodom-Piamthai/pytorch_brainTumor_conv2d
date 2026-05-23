for future user(most likely future me)
Dockerfile inside backend and frontend folder is for specifying how to build each part,like a blue print in parts
compose.yaml is to put the pieces together and run it together to ensure both part works as intended

build with:
docker compose up --build

once its build next run will be faster,no need for build:
docker compose up

stops with:
docker compose down