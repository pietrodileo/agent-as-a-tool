# Requirements

1. Create venv

`uv venv`

2. Activate venv (on Windows)

`.venv\Scripts\Activate`

3. Install requirements

`uv pip install -r requirements.txt`

4. clone langfuse github for selfhosting
Instructions can be found here: https://langfuse.com/self-hosting/deployment/docker-compose
Basically you should: 
-   Open a new VSCode window
-   git clone https://github.com/langfuse/langfuse.git
-   `cd langfuse`
-   `docker compose up`
-   Wait until the container is running, then go to http://localhost:3000
-   Subscribe to the service with a test account and create a test organization and project
-   Create new API keys and copy public and secret keys to the .env file

5. Install ollama
    https://ollama.com/download/windows

6. Install required model by opening terminal and running the command:
`ollama run "model"`
example: `ollama run qwen3.5`

7. run code
`uv run .\main.py`

# Configurations of .env file

My .env file to enable ollama or mistral ai and langfuse is configured in this way.
Please replace your API keys to use this code.

```
##############################
# GENERIC LLM CONFIGURATIONS #
##############################
MAX_TOKENS=1024
STREAMING=true                       # Enable streaming responses
TEMPERATURE=0.2                      # Temperature for response randomness (0.0 to 1.0)
THINK=false
MESSAGE_MEMORY=20
LLM_TYPE="mistral" # select which llm type to use (e.g., 'mistral' or 'ollama')

##########################
# MISTRAL CONFIGURATIONS #
##########################
MISTRAL_API_KEY="" 
MISTRAL_LLM_MODEL="mistral-medium-latest"        # Mistral model name (e.g., mistral-tiny, mistral-small, mistral-medium)
MISTRAL_BASE_URL="https://api.mistral.ai/v1/"

##########################
# OLLAMA CONFIGURATIONS #
##########################
OLLAMA_LLM_MODEL=qwen3.5:0.8b
OLLAMA_BASE_URL="http://localhost:11434"

###########################
# LANGFUSE CONFIGURATIONS #
###########################

# LOCAL CONFIGURATIONS
# LANGFUSE_SECRET_KEY=""
# LANGFUSE_PUBLIC_KEY=""
# LANGFUSE_BASE_URL="http://localhost:3000"

# CLOUD CONFIGURATIONS
LANGFUSE_SECRET_KEY=""
LANGFUSE_PUBLIC_KEY=""
LANGFUSE_BASE_URL="https://cloud.langfuse.com"

```
