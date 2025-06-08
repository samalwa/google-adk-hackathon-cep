# Data Science with Multiple Agents

## Overview

This project demonstrates a multi-agent system designed for sophisticated data analysis. It integrates several specialized agents to handle different aspects of the data pipeline, from data retrieval to advanced analytics and machine learning. The system is built to interact with BigQuery, perform complex data manipulations, generate data visualizations and execute machine learning tasks using BigQuery ML (BQML). The agent can generate text response as well as visuals, including plots and graphs for data analysis and exploration.



## Agent Details
The key features of the Data Science Multi-Agent include:

| Feature | Description |
| --- | --- |
| **Interaction Type:** | Conversational |
| **Complexity:**  | Advanced |
| **Agent Type:**  | Multi Agent |
| **Components:**  | Tools, AgentTools, Session Memory, RAG |
| **Vertical:**  | All (Applicable across industries needing advanced data analysis) |


### Architecture
![Multi Agent Architecture](Google-ADK-Hackathon.drawio)
!Flow Chart link https://app.eraser.io/workspace/lsnCZzokyxbNL47Z3GrT

### Key Features

*   **Multi-Agent Architecture:** Utilizes a top-level agent that orchestrates sub-agents, each specialized in a specific task.
*   **Database Interaction (NL2SQL):** Employs a Database Agent to interact with BigQuery using natural language queries, translating them into SQL.
*   **Segmentation & Activation (SG Agent):** Routes segmentation or activation requests on the database to the `sg_agent`.
*   **Sentiment Analysis Tool:** Uses the `call_st_agent` tool for sentiment analysis of text or transcribed content.
*   **Data Science Analysis (NL2Py):** Includes a Data Science Agent that performs data analysis and visualization using Python, based on natural language instructions.
*   **Machine Learning (BQML):** Features a BQML Agent that leverages BigQuery ML for training and evaluating machine learning models. Requests specifically for BQML are routed to the `bqml_agent` using the `call_bqml_agent` tool.
*   **GCS File Upload Tool:** Supports uploading files to Google Cloud Storage using the `upload_file_gcs_tool`.
*   **Content/Email Creation Tool:** Uses the `call_ct_agent` tool for creating and sending content or emails for marketing campaigns.
*   **Send Email Tool:** For sending emails, the `send_email` tool is used, requiring `email_html`, `recipient_email`, and `subject_line`.
*   **Code Interpreter Integration:** Supports the use of a Code Interpreter extension in Vertex AI for executing Python code, enabling complex data analysis and manipulation.
*   **ADK Web GUI:** Offers a user-friendly GUI interface for interacting with the agents.
*   **Testability:** Includes a comprehensive test suite for ensuring the reliability of the agents.

---

## Agent Routing & Tool Usage

The agent system is designed to intelligently route user requests to the appropriate sub-agent or tool based on intent:

1. **Intent Understanding & Routing**
    - If the user wants to work on the database, route to the `db_agent`.
    - If the user wants to perform segmentation or activation on the database, route to the `sg_agent`.
    - If the user wants to work with BigQuery ML, route to the `bqml_agent`.

2. **Sentiment Data Tool (`call_st_agent`):**
    - For sentiment analysis of content, use this tool.
    - If the content is not text, transcribe it first.
    - Always provide the content in text format.

3. **BigQuery ML Tool (`call_bqml_agent`):**
    - For explicit BigQuery ML requests, use this tool.
    - Provide a proper query, dataset, project ID, and context.

4. **GCS File Upload Tool (`upload_file_gcs_tool`):**
    - For uploading files to GCS buckets.
    - Provide `destination_blob_name`, file content (text), `content_type`, and context.

5. **Content/Email Creation Tool (`call_ct_agent`):**
    - For creating and sending content or emails for marketing campaigns.
    - Provide campaign description, audience nature, content type (email, message, etc.), and context.

6. **Send Email Tool (`send_email`):**
    - For sending emails, always provide `email_html`, `recipient_email`, and `subject_line`.
    - Display the HTML to the user and ask for confirmation before sending.
    - Check for recipient email in agent context and previous chats, and confirm with the user.
    - Send the email using the tool and provide a confirmation.

*   **ADK Web GUI:** Offers a user-friendly GUI interface for interacting with the agents.



## Setup and Installation

### Prerequisites

*   **Google Cloud Account:** You need a Google Cloud account with BigQuery enabled.
*   **Python 3.12+:** Ensure you have Python 3.12 or a later version installed.
*   **Poetry:** Install Poetry by following the instructions on the official Poetry website: [https://python-poetry.org/docs/](https://python-poetry.org/docs/)
*   **Git:** Ensure you have git installed. If not, you can download it from [https://git-scm.com/](https://git-scm.com/) and follow the [installation guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).



### Project Setup with Poetry

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/data-science
    ```

2.  **Install Dependencies with Poetry:**

    ```bash
    poetry install
    ```

    This command reads the `pyproject.toml` file and installs all the necessary dependencies into a virtual environment managed by Poetry.

3.  **Activate the Poetry Shell:**

    ```bash
    poetry env activate
    ```

    This activates the virtual environment, allowing you to run commands within the project's environment. To make sure the environment is active, use for example
    
    ```bash
    $> poetry env list
       data-science-FAlhSuLn-py3.13 (Activated)
    ```
    
    If the above command did not activate the environment for you, you can also activate it through

     ```bash
    source $(poetry env info --path)/bin/activate
    ```

4.  **Set up Environment Variables:**
    Rename the file ".env-example" to ".env"
    Fill the below values:

    ```bash
    # Choose Model Backend: 0 -> ML Dev, 1 -> Vertex
    GOOGLE_GENAI_USE_VERTEXAI=1

    # ML Dev backend config. Fill if using Ml Dev backend.
    GOOGLE_API_KEY='YOUR_VALUE_HERE'

    # Vertex backend config
    GOOGLE_CLOUD_PROJECT='YOUR_VALUE_HERE'
    GOOGLE_CLOUD_LOCATION='YOUR_VALUE_HERE'
    ```

    Follow the following steps to set up the remaining environment variables.

5.  **BigQuery Setup:**
    These steps will load the sample data provided in this repository to BigQuery.
    For our sample use case, we are working on the Forecasting Sticker Sales data from Kaggle:

    _Walter Reade and Elizabeth Park. Forecasting Sticker Sales. https://kaggle.com/competitions/playground-series-s5e1, 2025. Kaggle._

    *   First, set the BigQuery project ID in the `.env` file. This can be the same GCP Project you use for `GOOGLE_CLOUD_PROJECT`,
        but you can use other BigQuery projects as well, as long as you have access permissions to that project.
        If you have an existing BigQuery table you wish to connect, specify the `BQ_DATASET_ID` in the `.env` file as well.
        Make sure you leave `BQ_DATASET_ID='forecasting_sticker_sales'` if you wish to use the sample data.

        Alternatively, you can set the variables from your terminal:

        ```bash
        export BQ_PROJECT_ID='YOUR-BQ-PROJECT-ID'
        export BQ_DATASET_ID='YOUR-DATASET-ID' # leave as 'forecasting_sticker_sales' if using sample data
        ```

        You can skip the upload steps if you are using your own data. We recommend not adding any production critical datasets to this sample agent.
        If you wish to use the sample data, continue with the next step.

    *   You will find the datasets inside 'data-science/data_science/utils/data/'.
        Make sure you are still in the working directory (`agents/data-science`). To load the test and train tables into BigQuery, run the following commands:
        ```bash
        python3 data_science/utils/create_bq_table.py
        ```


6.  **BQML Setup:**
    The BQML Agent uses the Vertex AI RAG Engine to query the full BigQuery ML Reference Guide.

    Before running the setup, ensure your project ID is added in .env file: `"GOOGLE_CLOUD_PROJECT"`.
    Leave the corpus name empty in the .env file: `BQML_RAG_CORPUS_NAME = ''`. The corpus name will be added automatically once it's created.

    To set up the RAG Corpus for your project, run the methods `create_RAG_corpus()` and `ingest_files()` in
    `data-science/data_science/utils/reference_guide_RAG.py` by running the below command from the working directory:

    ```bash
    python3 data_science/utils/reference_guide_RAG.py
    ```


7.  **Other Environment Variables:**

    *   `NL2SQL_METHOD`: (Optional) Either `BASELINE` or `CHASE`. Sets the method for SQL Generation. Baseline uses Gemini off-the-shelf, whereas CHASE uses [CHASE-SQL](https://arxiv.org/abs/2410.01943)
    *   `CODE_INTERPRETER_EXTENSION_NAME`: (Optional) The full resource name of
        a pre-existing Code Interpreter extension in Vertex AI. If not provided,
        a new extension will be created. (e.g.,
        `projects/<YOUR_PROJECT_ID>/locations/<YOUR_LOCATION>/extensions/<YOUR_EXTENSION_ID>`).
        Check the logs/terminal for the ID of the newly created Code Interpreter
        Extension and provide the value in your environment variables to avoid
        creating multiple extensions.

    From the terminal:

    ```bash
    export CODE_INTERPRETER_EXTENSION_NAME='projects/<YOUR_PROJECT_ID>/locations/us-central1/extensions/<YOUR_EXTENSION_ID>'
    ```

## Running the Agent

You can run the agent using the ADK command in your terminal.
from the working directory:

1.  Run agent in CLI:

    ```bash
    poetry run adk run data_science
    ```

2.  Run agent with ADK Web UI:
    ```bash
    poetry run adk web
    ```
    Select the data_science from the dropdown




## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended for production use. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

This sample has not been rigorously tested, may contain bugs or limitations, and does not include features or optimizations typically required for a production environment (e.g., robust error handling, security measures, scalability, performance considerations, comprehensive logging, or advanced configuration options).

Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample. We recommend thorough review, testing, and the implementation of appropriate safeguards before using any derived agent in a live or critical system.
