# https://www.mapperinfluences.com/

Mapper influences backend code.

Uses MongoDB and Python FastAPI.

`/docs` for endpoint documentation.

If you have feature requests or bug reports, 
you can do so in [frontend repository](https://github.com/Fursum/mapper-influences-frontend) 
or in our [discord](https://discord.gg/SAwxBDe3Rf)
## How to run

#### Easiest way would be to use docker:
- Copy `.env.example` and change the name to `.env` 
- Fill it with your credentials.
- Use `docker compose up` to run the project..


You might only want to run database in docker, to do that just use `docker compose up mongo -d`


#### To run locally, do the first two steps from docker instructions and:
- Install python.
- Use `pip install -r requirements.txt` to install packages.
- `uvicorn app.main:app --host 0.0.0.0 --port 8000` to start the server.

You might want to use python virtual environments to avoid insalling packages system wide. 
Check out here: https://docs.python.org/3/library/venv.html

### How to run tests
If you can run the server locally using steps above, you can just type `pytest` and it will do its job.
