from __future__ import annotations

import json
from typing import Any

import google.auth
from google.auth.transport.requests import AuthorizedSession
import requests
import functions_framework

# Following GCP best practices, these credentials should be
# constructed at start-up time and used throughout
# https://cloud.google.com/apis/docs/client-libraries-best-practices
AUTH_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
CREDENTIALS, _ = google.auth.default(scopes=[AUTH_SCOPE])


def make_composer2_web_server_request(
    url: str, method: str = "GET", **kwargs: Any
) -> google.auth.transport.Response:
    """
    Make a request to Cloud Composer 2 environment's web server.
    Args:
      url: The URL to fetch.
      method: The request method to use ('GET', 'OPTIONS', 'HEAD', 'POST', 'PUT',
        'PATCH', 'DELETE')
      **kwargs: Any of the parameters defined for the request function:
                https://github.com/requests/requests/blob/master/requests/api.py
                  If no timeout is provided, it is set to 90 by default.
    """

    authed_session = AuthorizedSession(CREDENTIALS)

    # Set the default timeout, if missing
    if "timeout" not in kwargs:
        kwargs["timeout"] = 90

    return authed_session.request(method, url, **kwargs)


def trigger_dag(web_server_url: str, dag_id: str, data: dict) -> str:
    """
    Make a request to trigger a dag using the stable Airflow 2 REST API.
    https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html

    Args:
      web_server_url: The URL of the Airflow 2 web server.
      dag_id: The DAG ID.
      data: Additional configuration parameters for the DAG run (json).
    """

    endpoint = f"api/v1/dags/{dag_id}/dagRuns"
    request_url = f"{web_server_url}/{endpoint}"
    json_data = {"conf": data}

    response = make_composer2_web_server_request(
        request_url, method="POST", json=json_data
    )

    if response.status_code == 403:
        raise requests.HTTPError(
            "You do not have a permission to perform this operation. "
            "Check Airflow RBAC roles for your account."
            f"{response.headers} / {response.text}"
        )
    elif response.status_code != 200:
        response.raise_for_status()
    else:
        return response.text


@functions_framework.http
def trigger_dag_gcf(request):
    """
    HTTP Cloud Function to trigger a DAG.
    
    Args:
        request (flask.Request): The request object.
        
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
    """
    
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            request_json = request.get_json(silent=True)
            if request_json:
                # Extract parameters from JSON body
                bucket = request_json.get('bucket', 'YOUR-BUCKET-NAME')
                file_path = request_json.get('file', 'INPUT-PATH-TO-FILE')
            else:
                # Use default values
                bucket = 'YOUR-BUCKET-NAME'
                file_path = 'INPUT-PATH-TO-FILE'
        else:
            # Handle GET request with query parameters
            bucket = request.args.get('bucket', 'YOUR-BUCKET-NAME')
            file_path = request.args.get('file', 'INPUT-PATH-TO-FILE')

        # TODO(developer): replace with your values
        # Replace web_server_url with the Airflow web server address
        web_server_url = (
            "YOUR-WEB-SERVER-URL"
        )
        # Replace with the ID of the DAG that you want to run
        dag_id = 'gcs_dataflow_bigquery_official'

        dag_conf = {
            "bucket": bucket,
            "file": file_path
        }

        # Trigger the DAG
        response_text = trigger_dag(web_server_url, dag_id, dag_conf)
        
        return {
            'status': 'success',
            'message': 'DAG triggered successfully',
            'dag_id': dag_id,
            'dag_conf': dag_conf,
            'response': response_text
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to trigger DAG: {str(e)}'
        }, 500
