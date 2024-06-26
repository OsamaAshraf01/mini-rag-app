# mini-rag-app

This is a minimal implementation of the RAG model for question answering.



## Requirements
- Python 3.8 or later

#### Install Python using MiniConda
1) Donload and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/index.html)
2) Create a new environment using the following command:
```bash
$ conda create -n mini-rag-app python=3.8
```
3) Activate the environment:
```bash
$ conda activate mini-rag-app
```


### (Optional) Setup your command line interface for better readability
```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```


## Installation

### Install the required packages
```bash
$ pip install -r src/requirements.txt
```

### Setup the environment variables
```bash
$ cp .env.example .env
```
Then, set your environment variables in the `.env` file. like `OPENAI_KEY` value


## Run the FastAPI Server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## POSTMAN Collection

Download the POSTMAN collection from [/assets/mini-rag-app.postman_collection.json](/assets/mini-rag-app.postman_collection.json)
