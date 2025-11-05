# AIPOM: Agent-aware Interactive Planning for Multi-Agent Systems

[![Conference](https://img.shields.io/badge/EMNLP_Demo-2025-cornflowerblue)](https://aclanthology.org/2025.emnlp-demos.7.pdf)
[![arXiv](https://img.shields.io/badge/arxiv-2509.24826-firebrick)](https://arxiv.org/abs/2509.24826)

**AIPOM** is designed for **human-LLM collaborative planning** in orchestrated **multi-agent systems**. It addresses the lack of transparency and controllability in existing LLM-based planning systems by combining natural language interaction with a visual, interactive plan graph.

Please refer to the [AIPOM paper](https://aclanthology.org/2025.emnlp-demos.7.pdf) for the full system details and implementation.

## 🎬 Demo Video

Click below 🖼️ to see **AIPOM** in action:

[![Demo video](https://meganno.s3.us-east-1.amazonaws.com/aipom-teaser.png)](https://www.youtube.com/watch?v=Djd-gen2Xjs)

## 🏛️ System Architecture

AIPOM is built with a React frontend and a Python backend (FastAPI).
- **Backend**: Handles planning & agent orchestration.
- **Frontend**: Dual-panel interface
  - **Chat Panel**: natural language interaction
  - **Plan Panel**: interactive plan graph showing intermediate outputs and agent dependencies, enabling direct manipulation


## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- An OpenAI API key
- (Optional, for development) Node.js & npm

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/rit-git/aipom.git
    cd aipom
    ```

2. Create environment and install Python dependencies:
    ```bash
    conda create -n aipom python=3.10
    conda activate aipom
    pip install -r requirements.txt
    ```

3. Set OpenAI API key:
    ```bash
    export OPENAI_API_KEY="your-api-key-here"
    ```

## ▶️ Usage

### Regular Usage

1. Start the backend (serves pre-built frontend):
    ```bash
    python server.py
    ```
2. Open your browser and go to [http://localhost:8000](http://localhost:8000).

- In case of `ERROR: [Errno 48] Address already in use` while running server:
    ```bash
    sudo lsof -i:8000
    kill -9 PID
    ```

**If you encounter any issues or the system is not responding, try refreshing your browser.**

### (Optional) Frontend Development Mode

1. Start the backend:
    ```bash
    python server.py
    ```
2. In a **separate** terminal, start the frontend development server. This allows hot-reloading of React components while the backend is running.
    ```bash
    cd frontend
    npm install        # if not already installed
    npm run dev
    ```
3. Open your browser and go to [http://localhost:5173](http://localhost:5173).

## 🤖 Available Agents

AIPOM includes a set of specialized agents for various tasks. Some examples of built-in agents:

- Mathematical: ```add```, ```subtract```, ```multiply```, ```divide```, and LLM-powered variants.
- Text: ```extract```, ```summarize```, ```compare```
- Other: ```web_search``` (powered by Google Custom Search API), ```identify_operands```, ```filter```, ```fallback``` (commonsense agent handling queries that do not match any specific operation).

> **Note:**  
> The `web_search` agent is currently **disabled** by default.  
> To enable it:  
> 1. Set the environment variables `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`.  
> 2. Uncomment the `web_search` agent lines in `agent_registry.py`.

### Extending Agents

You can easily add new agents:
1. Create a new agent file in the ```/agents``` directory.
2. Register your agent in ```agent_registry.py``` with a short description.
Once registered, your new agent will be available for use alongside the built-in agents.


## 📄 License

This project is licensed under the BSD 3-Clause License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Disclosures:

This software may include, incorporate, or access open source software (OSS) components, datasets and other third party components, including those identified below. The license terms respectively governing the datasets and third-party components continue to govern those portions, and you agree to those license terms may limit any distribution, use, and copying. You may use any OSS components under the terms of their respective licenses, which may include BSD 3, Apache 2.0, and other licenses. In the event of conflicts between Megagon Labs, Inc. (“Megagon”) license conditions and the OSS license conditions, the applicable OSS conditions governing the corresponding OSS components shall prevail. You agree not to, and are not permitted to, distribute actual datasets used with the OSS components listed below. You agree and are limited to distribute only links to datasets from known sources by listing them in the datasets overview table below. You agree that any right to modify datasets originating from parties other than Megagon are governed by the respective third party’s license conditions. You agree that Megagon grants no license as to any of its intellectual property and patent rights. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS (INCLUDING MEGAGON) “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. You agree to cease using, incorporating, and distributing any part of the provided materials if you do not agree with the terms or the lack of any warranty herein. While Megagon makes commercially reasonable efforts to ensure that citations in this document are complete and accurate, errors may occur. If you see any error or omission, please help us improve this document by sending information to contact_oss@megagon.ai.

### Datasets

All datasets used within the product are listed below (including their copyright holders and the license information).

For Datasets having different portions released under different licenses, please refer to the included source link specified for each of the respective datasets for identifications of dataset files released under the identified licenses.

</br>


| ID  | OSS Component Name | Modified | Copyright Holder | Upstream Link | License  |
|-----|----------------------------------|----------|------------------|-----------------------------------------------------------------------------------------------------------|--------------------|
| 1 | Grade School Math GSM8K | No | Copyright (c) 2021 OpenAI | [link](https://github.com/openai/grade-school-math) | MIT License
| 2 | Multi-step Arithmetic (BIG-Bench Hard) | No | Copyright (c) 2022 suzgunmirac | [link](https://huggingface.co/datasets/maveriq/bigbenchhard/viewer/multistep_arithmetic_two?views%5B%5D=multistep_arithmetic_two) | MIT License

## 📚 Citation

```bibtex
@inproceedings{kim-etal-2025-aipom,
    title = "{AIPOM}: Agent-aware Interactive Planning for Multi-Agent Systems",
    author = "Kim, Hannah and Mitra, Kushan and Shen, Chen and Zhang, Dan and Hruschka, Estevam",
    booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: System Demonstrations",
    month = nov,
    year = "2025",
    url = "https://aclanthology.org/2025.emnlp-demos.7/",
    pages = "85--96"
}
```