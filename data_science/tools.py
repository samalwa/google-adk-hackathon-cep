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

"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""
from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError
from google.adk.tools import ToolContext, FunctionTool
from data_science.utils.utils import get_env_var
from typing import Dict, Any, Optional
import logging
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

#from .sub_agents import ds_agent, db_agent
from .sub_agents import db_agent,st_agent,ct_agent


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    agent_tool = AgentTool(agent=db_agent)

    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output

async def call_st_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call sentiment agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    agent_tool = AgentTool(agent=st_agent)

    st_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["st_agent_output"] = st_agent_output
    return st_agent_output

async def call_ds_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call data science (nl2py) agent."""

    if question == "N/A":
        return tool_context.state["db_agent_output"]

    input_data = tool_context.state["query_result"]

    question_with_data = f"""
  Question to answer: {question}

  Actual data to analyze prevoius quesiton is already in the following:
  {input_data}

  """

    agent_tool = AgentTool(agent=ds_agent)

    ds_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    tool_context.state["ds_agent_output"] = ds_agent_output
    return ds_agent_output


async def call_ct_agent(
    question: str,
    campaign_desc: str,
    audient_behaviour_desc: str,
    content_type: str,
    tool_context: ToolContext,
):
    """Tool to call content creator agent."""

    question_with_data = f"""
  context: {question}

  
 audient_behaviour_description: {audient_behaviour_desc}
campaign_description : {campaign_desc}
content type : {content_type}

  """

    agent_tool = AgentTool(agent=ct_agent)

    ct_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    tool_context.state["ct_agent_output"] = ct_agent_output
    return ct_agent_output

def upload_file_to_gcs(
    tool_context: ToolContext,
    file_content: str,
    bucket_name: Optional[str] = get_env_var("BQ_BUCKET_ID"),
    destination_blob_name: Optional[str] = None,
    content_type: Optional[str] = "text/plain"
) -> Dict[str, Any]:
    """
    Uploads a file from ADK artifacts to a Google Cloud Storage bucket.
    
    Args:
        tool_context: The tool context for ADK
        bucket_name: The name of the GCS bucket to upload to
        file_artifact_name: The name of the artifact file in the ADK session
        destination_blob_name: The name to give the file in GCS (defaults to artifact name)
        content_type: The content type of the file (defaults to PDF)
        
    Returns:
        A dictionary containing the upload status and details
    """
    if content_type is None:
        content_type = GCS_DEFAULT_CONTENT_TYPE
    try:
        # Check if user_content contains a PDF attachment
                
        # if (hasattr(tool_context, "user_content") and 
        #     tool_context.user_content and 
        #     tool_context.user_content.parts):
            
            # Look for any file in parts
            # file_data = None
            # for part in tool_context.user_content.parts:
            #     if hasattr(part, "inline_data") and part.inline_data:
            #         if part.inline_data.mime_type.startswith("application/"):
            #             file_data = part.inline_data.data
            #             break
            #         if part.inline_data.mime_type.startswith("text/"):
            #             file_data = part.inline_data.data
            #             break    
            # if file_data:
            #     # We found file data in the user message
            #     if not destination_blob_name:
            #         destination_blob_name = file_artifact_name
            #         if content_type == "application/pdf" and not destination_blob_name.lower().endswith(".pdf"):
            #             destination_blob_name += ".pdf"
                
                # Upload to GCS
        file_data=file_content
        client = storage.Client(project=get_env_var("BQ_PROJECT_ID"))
        bucket = client.bucket(bucket_name)
        destination_blob_name = f"unstructureddatasfdc/transcripts/{destination_blob_name}" #specify destination path
        blob = bucket.blob(destination_blob_name)
        print("DEBUG file_data ", file_data) 
        blob.upload_from_string(
            data=file_data,
            content_type=content_type
        )
        
        # Generate a URL
        try:
            print("Not generating public URL")
            url=f"gs://{bucket_name}/{destination_blob_name}"
            #url = blob.public_url
        except:
            url = f"gs://{bucket_name}/{destination_blob_name}"
        
        return {
            "status": "success",
            "bucket": bucket_name,
            "filename": destination_blob_name,
            "gcs_uri": f"gs://{bucket_name}/{destination_blob_name}",
            "size_bytes": len(file_data),
            "content_type": content_type,
            "url": url,
            "message": f"Successfully uploaded file to gs://{bucket_name}/{destination_blob_name}"
        }
        
        # If no file found in user content, return error
        return {
            "status": "error",
            "message": "No file found in the current message. Please upload a file and try again.",
            "details": "Files must be attached directly to the current message."
        }
    except GoogleAPIError as e:
        return {
            "status": "error",
            "error_message": str(e),
            "message": f"Failed to upload file: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "message": f"An unexpected error occurred: {str(e)}"
        }
upload_file_gcs_tool = FunctionTool(upload_file_to_gcs)     