
1. Create venv

uv venv

2. Activate venv (on Windows)

.venv\Scripts\Activate

3. Install requirements

uv pip install -r requirements.txt

4. clone langfuse github for selfhosting
Instructions can be found here: https://langfuse.com/self-hosting/deployment/docker-compose
Basically you should: 
-   Open a new VSCode window
-   git clone https://github.com/langfuse/langfuse.git
-   cd langfuse
-   docker compose up
-   Wait until the container is running, then go to http://localhost:3000
-   Subscribe to the service with a test account and create a test organization and project
-   Create new API keys and copy public and secret keys to the .env file

5. Install ollama
    https://ollama.com/download/windows

6. Install required model by opening terminal and running the command:
ollama run "model"
example: ollama run qwen3.5

7. run code
uv run .\main.py
