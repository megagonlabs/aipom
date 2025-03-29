# Interactive Planning for Orchestrated Multi-Agent Systems

**AIPOM** is a system that integrates natural language interaction with direct manipulation of plan graphs to support human-in-the-loop planning in orchestrated multi-agent systems (OMAS). The system enables users to transparently inspect, refine, and collaboratively guide LLM-generated plans, enhancing user control and trust in multi-agent workflows.

*This code is accompanying a paper submission to the ACL 2025 System Demonstration. It represents a limited version of the original system, tailored for math reasoning problems, with a subset of agents due to external API access issues. Please refer to the paper for the full system details and implementation.*


## 🎬 Demo Video

Click below 🖼️ to see **AIPOM** in action:

[![Demo video](https://meganno.s3.us-east-1.amazonaws.com/aipom-teaser.png)](https://meganno.s3.us-east-1.amazonaws.com/acl-2025-demo-video.mp4)


## Prerequisites
Before installing, make sure you have the following installed:
- **Python** (version 3.8 or higher)
- **Node.js** (version 16 or higher)
- **npm** (version 7 or higher)

### OpenAI API Key
**AIPOM** is powered by GPT, and requires an OpenAI API key and organization to use the system. You need to set these values before running the project.

1. In your terminal, run the following commands to set your **OpenAI API key** and **organization ID**:
    ```bash
    export OPENAI_API_KEY="your-api-key-here"
    export OPENAI_ORGANIZATION="your-organization-id-here"
    ```

2. Verify that the environment variables are set correctly by running:
    ```bash
    echo $OPENAI_API_KEY
    echo $OPENAI_ORGANIZATION
    ```


## Installation

### Backend (Python)
1. Clone the repository:
    ```bash
    git clone https://github.com/rit-git/aipom.git
    cd aipom
    ```

2. Create conda env
    ```bash
    conda create -n <env_name> python=3.12.3
    ```

3. Install the required Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Frontend (React)
1. Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2. Install the required Node.js dependencies:
    ```bash
    npm install
    ```


## Usage
To start the development environment, run both the Python backend and React frontend in separate terminals:

### Terminal 1: Start the Python backend server
```bash
python server.py
```
This starts the backend server, which handles the logic for plan generation, refinement, and agent coordination.

In case of `ERROR: [Errno 48] Address already in use` while running server
```bash
> sudo lsof -i:8000
> kill -9 PID
```

### Terminal 2: Start the React frontend server
```bash
cd frontend
npm run dev
```
This starts the frontend server.
Open your browser and go to [http://localhost:5173](http://localhost:5173).

**If you encounter any issues or the system is not responding, try refreshing your browser.**

## Guidelines

We recommend following the guidelines below, for testing our system prototype:

1. Restrict query to math reasoning questions
2. While configuring agent params, restrict `model` to one of [`gpt-4o`, `gpt-4o-mini`]