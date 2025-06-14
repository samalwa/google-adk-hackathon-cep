# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import os
from google.cloud import bigquery
from vertexai import rag
import datetime

MAX_NUM_ROWS=50
def check_bq_models(dataset_id: str) -> str:
    """Lists models in a BigQuery dataset and returns them as a string.

    Args:
        dataset_id: The ID of the BigQuery dataset (e.g., "project.dataset").

    Returns:
        A string representation of a list of dictionaries, where each dictionary
        contains the 'name' and 'type' of a model in the specified dataset.
        Returns an empty string "[]" if no models are found.
    """

    try:
        client = bigquery.Client()

        models = client.list_models(dataset_id)
        model_list = []  # Initialize as a list

        print(f"Models contained in '{dataset_id}':")
        for model in models:
            model_id = model.model_id
            model_type = model.model_type
            model_list.append({"name": model_id, "type": model_type})

        return str(model_list)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def get_model_features(model_id: str,):

    # Construct a BigQuery client object.
    client = bigquery.Client()
    bqml_code = """
        SELECT
        *
        FROM
        ML.FEATURE_INFO(MODEL `{model_id}`)
        """
    query_job = client.query(bqml_code)
    results=query_job.result()
    final_result = {"query_result": None, "error_message": None}
    if results.schema:  # Check if query returned data
            rows = [
                {
                    key: (
                        value
                        if not isinstance(value, datetime.date)
                        else value.strftime("%Y-%m-%d")
                    )
                    for (key, value) in row.items()
                }
                for row in results
            ][
                :MAX_NUM_ROWS
            ]  # Convert BigQuery RowIterator to list of dicts
            # return f"Valid SQL. Results: {rows}"
            final_result["query_result"] = rows
    return final_result

def execute_bqml_code(bqml_code: str, project_id: str, dataset_id: str) -> str:
    """
    Executes BigQuery ML code.
    """

    # timeout_seconds = 1500

    client = bigquery.Client(project=project_id)

    try:
        bqml_query_job = client.query(bqml_code)
        start_time = time.time()

        while not bqml_query_job.done():
            elapsed_time = time.time() - start_time
            # if elapsed_time > timeout_seconds:
            #     return (
            #         "Timeout: BigQuery job did not complete within"
            #         f" {timeout_seconds} seconds. Job ID: {query_job.job_id}"
            #     )

            print(
                f"Query Job Status: {bqml_query_job.state}, Elapsed Time:"
                f" {elapsed_time:.2f} seconds. Job ID: {bqml_query_job.job_id}"
            )
            time.sleep(5)

        if bqml_query_job.error_result:
            return f"Error executing BigQuery ML code: {bqml_query_job.error_result}"

        if bqml_query_job.exception():
            return f"Exception during BigQuery ML execution: {bqml_query_job.exception()}"

        results = bqml_query_job.result()
        counter = 0
        if results.total_rows > 0:
            result_string = ""
            for row in results:
                result_string += str(dict(row.items())) + "\n"
                counter+=1
                if counter>50:
                    break
            return f"BigQuery ML code executed successfully. Results:\n{result_string}"
        else:
            return "BigQuery ML code executed successfully."

    except Exception as e:
        return f"An error occurred: {str(e)}"


def rag_response(query: str) -> str:
    """Retrieves contextually relevant information from a RAG corpus.

    Args:
        query (str): The query string to search within the corpus.

    Returns:
        vertexai.rag.RagRetrievalQueryResponse: The response containing retrieved
        information from the corpus.
    """
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=corpus_name,
            )
        ],
        text=query,
        rag_retrieval_config=rag_retrieval_config,
    )
    return str(response)
