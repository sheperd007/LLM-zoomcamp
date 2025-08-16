# IT Group Assistant

<p align="center">
  <img src="images/banner.jpg">
</p>

IT teams often face challenges with knowledge management and quick access to technical information. Documentation can be scattered, outdated, or difficult to search through, making it hard to provide timely support to users and resolve technical issues efficiently.

The IT Group Assistant provides a conversational AI that helps IT professionals quickly access technical knowledge, troubleshoot issues, and find solutions, making IT support more efficient and accessible.

This project was implemented for 
[LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp) -
a free course about LLMs and RAG.

## Project overview

The IT Group Assistant is a RAG application designed to assist
IT professionals with technical knowledge and troubleshooting.

The main use cases include:

1. Technical Knowledge Retrieval: Finding information about IT concepts, technologies, and best practices.
2. Troubleshooting Support: Providing guidance for common IT issues and their solutions.
3. Technology Explanations: Explaining technical concepts in an accessible way.
4. Conversational Interaction: Making it easy to get technical information without sifting through documentation or knowledge bases.

## Dataset

The dataset used in this project contains synthetic IT-related knowledge items, including:

- **Title:** Knowledge item topic.
- **Text:** Knowledge item text from a LLM.
- **Alternative Text:** Alternative Information from another LLM


The dataset was sourced from [Kaggle's Synthetic IT-Related Knowledge Items](https://www.kaggle.com/datasets/dkhundley/synthetic-it-related-knowledge-items) and serves as the foundation for the IT Group Assistant's knowledge retrieval and technical support capabilities.

You can find the data in [`data/data.csv`](data/data.csv).

## Technologies

- Python 3.12
- Docker and Docker Compose for containerization
- [Minsearch](https://github.com/alexeygrigorev/minsearch) for full-text search
- FastAPI as the API interface (see [Background](#background) for more information on FastAPI)
- Grafana for monitoring and PostgreSQL as the backend for it
- OpenAI as an LLM

## Preparation

Since we use OpenAI, you need to provide the API key:

1. Install `direnv`. If you use Ubuntu, run `sudo apt install direnv` and then `direnv hook bash >> ~/.bashrc`.
2. Copy `.envrc_template` into `.envrc` and insert your key there.
3. For OpenAI, it's recommended to create a new project and use a separate key.
4. Run `direnv allow` to load the key into your environment.

For dependency management, we use pipenv, so you need to install it:

```bash
pip install pipenv
```

Once installed, you can install the app dependencies:

```bash
pipenv install --dev
```

## Running the application

### Database configuration

Before the application starts for the first time, the database
needs to be initialized.

First, run `postgres`:

```bash
docker-compose up postgres
```

Then run the [`db_prep.py`](IT_team_assistance/db_prep.py) script:

```bash
pipenv shell

cd IT_team_assistance

export POSTGRES_HOST=localhost
python db_prep.py
```

To check the content of the database, use `pgcli` (already
installed with pipenv):

```bash
pipenv run pgcli -h localhost -U your_username -d course_assistant -W
```

You can view the schema using the `\d` command:

```sql
\d conversations;
```

And select from this table:

```sql
select * from conversations;
```

### Running with Docker-Compose

The easiest way to run the application is with `docker-compose`:

```bash
docker-compose up
```

### Running locally

If you want to run the application locally,
start only postres and grafana:

```bash
docker-compose up postgres grafana
```

If you previously started all applications with
`docker-compose up`, you need to stop the `app`:

```bash
docker-compose stop app
```

Now run the app on your host machine:

```bash
pipenv shell

cd IT_team_assistance

export POSTGRES_HOST=localhost
python app.py
```

### Running with Docker (without compose)

Sometimes you might want to run the application in
Docker without Docker Compose, e.g., for debugging purposes.

First, prepare the environment by running Docker Compose
as in the previous section.

Next, build the image:

```bash
docker build -t it-assistant .
```

And run it:

```bash
docker run -it --rm \
    --network="it-assistant_default" \
    --env-file=".env" \
    -e OPENAI_API_KEY=${OPENAI_API_KEY} \
    -e DATA_PATH="data/data.csv" \
    -p 5000:5000 \
    it-assistant
```

### Time configuration

When inserting logs into the database, ensure the timestamps are
correct. Otherwise, they won't be displayed accurately in Grafana.

When you start the application, you will see the following in
your logs:

```
Database timezone: Asia/Muscat
Database current time (Muscat): 2024-08-24 06:43:12.169624+00:00
Database current time (Asia/Muscat): 2024-08-24 08:43:12.169624+02:00
Python current time: 2024-08-24 08:43:12.170246+02:00
Inserted time (Muscat): 2024-08-24 06:43:12.170246+00:00
Inserted time (Asia/Muscat): 2024-08-24 08:43:12.170246+02:00
Selected time (Muscat): 2024-08-24 06:43:12.170246+00:00
Selected time (Asia/Muscat): 2024-08-24 08:43:12.170246+02:00
```

Make sure the time is correct.

You can change the timezone by replacing `TZ` in `.env`.

On some systems, specifically WSL, the clock in Docker may get
out of sync with the host system. You can check that by running:

```bash
docker run ubuntu date
```

If the time doesn't match yours, you need to sync the clock:

```bash
wsl

sudo apt install ntpdate
sudo ntpdate time.windows.com
```

Note that the time is in Asia/Muscat.

After that, start the application (and the database) again.

## Using the application

When the application is running, we can start using it.

### CLI

We built an interactive CLI application using
[questionary](https://questionary.readthedocs.io/en/stable/).

To start it, run:

```bash
pipenv run python cli.py
```

You can also make it randomly select a question from
[our ground truth dataset](data/ground-truth-retrieval.csv):

```bash
pipenv run python cli.py --random
```

### Using `requests`

When the application is running, you can use
[requests](https://requests.readthedocs.io/en/latest/)
to send questions—use [test.py](test.py) for testing it:

```bash
pipenv run python test.py
```

It will pick a random question from the ground truth dataset
and send it to the app.

### CURL

You can also use `curl` for interacting with the API:

```bash
URL=http://localhost:5000
QUESTION="How do I troubleshoot Docker container networking issues?"
DATA='{
    "question": "'${QUESTION}'"
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${DATA}" \
    ${URL}/question
```

You will see something like the following in the response:

```json
{
    "answer": "To troubleshoot Docker container networking issues, you can follow these steps: 1) Check if the container is running with 'docker ps', 2) Inspect the container's network configuration with 'docker inspect <container_name>', 3) Verify network connectivity using 'docker exec <container_name> ping <target>', 4) Check if ports are properly exposed and mapped, 5) Review Docker network settings with 'docker network ls' and 'docker network inspect <network_name>'. Common issues include incorrect port mappings, network mode configuration, or firewall rules blocking connections.",
    "conversation_id": "4e1cef04-bfd9-4a2c-9cdd-2771d8f70e4d",
    "question": "How do I troubleshoot Docker container networking issues?"
}
```

Sending feedback:

```bash
ID="4e1cef04-bfd9-4a2c-9cdd-2771d8f70e4d"
URL=http://localhost:5000
FEEDBACK_DATA='{
    "conversation_id": "'${ID}'",
    "feedback": 1
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${FEEDBACK_DATA}" \
    ${URL}/feedback
```

After sending it, you'll receive the acknowledgement:

```json
{
    "message": "Feedback received for conversation 4e1cef04-bfd9-4a2c-9cdd-2771d8f70e4d: 1"
}
```

## Code

The code for the application is in the [`IT_team_assistance`](IT_team_assistance/) folder:

- [`app.py`](IT_team_assistance/app.py) - the FastAPI API, the main entrypoint to the application
- [`rag.py`](IT_team_assistance/rag.py) - the main RAG logic for building the retrieving the data and building the prompt
- [`ingest.py`](IT_team_assistance/ingest.py) - loading the data into the knowledge base
- [`minsearch.py`](IT_team_assistance/minsearch.py) - an in-memory search engine
- [`db.py`](IT_team_assistance/db.py) - the logic for logging the requests and responses to postgres
- [`db_prep.py`](IT_team_assistance/db_prep.py) - the script for initializing the database

We also have some code in the project root directory:

- [`test.py`](test.py) - select a random question for testing
- [`cli.py`](cli.py) - interactive CLI for the APP

### Interface

We use FastAPI for serving the application as an API.

Refer to the ["Using the Application" section](#using-the-application)
for examples on how to interact with the application.

### Ingestion

The ingestion script is in [`ingest.py`](IT_team_assistance/ingest.py).

Since we use an in-memory database, `minsearch`, as our
knowledge base, we run the ingestion script at the startup
of the application.

It's executed inside [`rag.py`](IT_team_assistance/rag.py)
when we import it.

### Retrieval evaluation

The basic approach - using `minsearch` without any boosting - gave the following metrics:

- Hit rate: 94%
- MRR: 82%

The improved version (with tuned boosting):

- Hit rate: 94%
- MRR: 90%

The best boosting parameters:

```python
boost = {
    'Title': 1.5,
    'Text': 1,
    'alt_Text': 1
}
```

### RAG flow evaluation

We used the LLM-as-a-Judge metric to evaluate the quality
of our RAG flow.

For `gpt-4o-mini`, in a sample with 200 records, we had:

- 167 (83%) `RELEVANT`
- 30 (15%) `PARTLY_RELEVANT`
- 3 (1.5%) `NON_RELEVANT`

We also tested `gpt-4o`:

- 168 (84%) `RELEVANT`
- 30 (15%) `PARTLY_RELEVANT`
- 2 (1%) `NON_RELEVANT`

The difference is minimal, so we opted for `gpt-4o-mini`.

## Monitoring

We use Grafana for monitoring the application. 

It's accessible at [localhost:3000](http://localhost:3000):

- Login: "admin"
- Password: "admin"

The monitoring dashboard contains several panels:

1. **Last 5 Conversations (Table):** Displays a table showing the five most recent conversations, including details such as the question, answer, relevance, and timestamp. This panel helps monitor recent interactions with users.
2. **+1/-1 (Pie Chart):** A pie chart that visualizes the feedback from users, showing the count of positive (thumbs up) and negative (thumbs down) feedback received. This panel helps track user satisfaction.
3. **Relevancy (Gauge):** A gauge chart representing the relevance of the responses provided during conversations. The chart categorizes relevance and indicates thresholds using different colors to highlight varying levels of response quality.
4. **OpenAI Cost (Time Series):** A time series line chart depicting the cost associated with OpenAI usage over time. This panel helps monitor and analyze the expenditure linked to the AI model's usage.
5. **Tokens (Time Series):** Another time series chart that tracks the number of tokens used in conversations over time. This helps to understand the usage patterns and the volume of data processed.
6. **Model Used (Bar Chart):** A bar chart displaying the count of conversations based on the different models used. This panel provides insights into which AI models are most frequently used.
7. **Response Time (Time Series):** A time series chart showing the response time of conversations over time. This panel is useful for identifying performance issues and ensuring the system's responsiveness.

### Setting up Grafana

All Grafana configurations are in the [`grafana`](grafana/) folder:

- [`init.py`](grafana/init.py) - for initializing the datasource and the dashboard.
- [`dashboard.json`](grafana/dashboard.json) - the actual dashboard (taken from LLM Zoomcamp without changes).

To initialize the dashboard, first ensure Grafana is
running (it starts automatically when you do `docker-compose up`).

Then run:

```bash
pipenv shell

cd grafana

# make sure the POSTGRES_HOST variable is not overwritten 
env | grep POSTGRES_HOST

python init.py
```

Then go to [localhost:3000](http://localhost:3000):

- Login: "admin"
- Password: "admin"

When prompted, keep "admin" as the new password.

## Background

Here we provide background on some tech not used in the
course and links for further reading.

### FastAPI

We use FastAPI for creating the API interface for our application.
It's a modern, fast web framework for building APIs with Python: we can easily
create an endpoint for asking questions and use web clients
(like `curl` or `requests`) for communicating with it.

In our case, we can send questions to `http://localhost:5000/question`.

For more information, visit the [official FastAPI documentation](https://fastapi.tiangolo.com/).

