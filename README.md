# Cloud Function DAG Trigger

A Google Cloud Function that triggers Apache Airflow DAGs in Google Cloud Composer environments. This serverless solution provides a simple HTTP endpoint to initiate data processing workflows.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🌟 Overview

This Cloud Function serves as a bridge between external systems and Google Cloud Composer (Apache Airflow). It allows you to trigger DAGs programmatically via HTTP requests, making it ideal for:

- **Event-driven workflows**: Trigger data processing when files are uploaded
- **Scheduled integrations**: Initiate workflows from external schedulers
- **Manual triggers**: Provide a simple API for manual DAG execution
- **Microservices architecture**: Decouple workflow triggering from business logic

### Key Features

- ✅ **Serverless**: No infrastructure management required
- ✅ **Authenticated**: Uses Google Cloud IAM for secure access
- ✅ **Flexible**: Supports custom DAG configurations
- ✅ **Scalable**: Automatically scales with demand
- ✅ **Cost-effective**: Pay only for actual usage

## 🏗️ Architecture

```
┌─────────────────┐    HTTP POST    ┌─────────────────┐    REST API    ┌─────────────────┐
│   Client App    │ ──────────────→ │ Cloud Function  │ ──────────────→ │ Cloud Composer  │
│                 │                 │                 │                 │   (Airflow)     │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │   DAG Execution │
                                    │                 │
                                    └─────────────────┘
```

## 🔧 Prerequisites

Before deploying this Cloud Function, ensure you have:

### Google Cloud Setup
- **Google Cloud Project** with billing enabled
- **Cloud Functions API** enabled
- **Cloud Composer API** enabled
- **IAM permissions** for deploying functions and accessing Composer

### Required APIs
```bash
# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable composer.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Tools Installation
- **Google Cloud SDK** (gcloud CLI)
- **Python 3.9+** for local development
- **Git** for version control

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd cloud-function-dag-trigger
```

### 2. Review the Code Structure
```
├── main.py              # Cloud Function code
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gcloudignore       # Files to ignore during deployment
```

### 3. Update Configuration
Edit `main.py` to update your specific settings:

```python
# Update these values in main.py
web_server_url = "https://YOUR-COMPOSER-URL"
dag_id = 'your-dag-id'
```

### 4. Deploy the Function
```bash
# Deploy the Cloud Function
gcloud functions deploy trigger-dag-function \
    --runtime python39 \
    --trigger-http \
    --entry-point trigger_dag_gcf \
    --timeout 540s \
    --memory 512MB \
    --allow-unauthenticated \
    --region us-central1
```

## ⚙️ Configuration

### Environment Variables
Set these in your deployment or via the Google Cloud Console:

| Variable | Description | Example |
|----------|-------------|---------|
| `COMPOSER_WEB_SERVER_URL` | Airflow web server URL | `https://xxx-dot-us-central1.composer.googleusercontent.com` |
| `DEFAULT_DAG_ID` | Default DAG to trigger | `gcs_dataflow_bigquery_official` |
| `DEFAULT_BUCKET` | Default GCS bucket | `us-central1-dev-bucket` |

### IAM Permissions
The Cloud Function needs these permissions:

```json
{
  "bindings": [
    {
      "role": "roles/composer.user",
      "members": [
        "serviceAccount:your-function-service-account@project.iam.gserviceaccount.com"
      ]
    }
  ]
}
```

### Composer Configuration
Ensure your Composer environment has:
- **Airflow 2.x** (for REST API support)
- **RBAC enabled** with appropriate user permissions
- **Network connectivity** to the Cloud Function

## 📖 Usage

### Basic Usage

**Trigger DAG with Default Settings:**
```bash
curl -X POST https://YOUR-REGION-PROJECT.cloudfunctions.net/trigger-dag-function
```

**Trigger DAG with Custom Parameters:**
```bash
curl -X POST https://YOUR-REGION-PROJECT.cloudfunctions.net/trigger-dag-function \
  -H "Content-Type: application/json" \
  -d '{
    "bucket": "my-data-bucket",
    "file": "data/input/processed-data.csv"
  }'
```

### Advanced Usage

**Using GET Request with Query Parameters:**
```bash
curl "https://YOUR-REGION-PROJECT.cloudfunctions.net/trigger-dag-function?bucket=my-bucket&file=data/input/file.csv"
```

**From Python Application:**
```python
import requests

url = "https://YOUR-REGION-PROJECT.cloudfunctions.net/trigger-dag-function"
payload = {
    "bucket": "my-data-bucket",
    "file": "data/input/dataset.csv"
}

response = requests.post(url, json=payload)
print(response.json())
```

**From JavaScript Application:**
```javascript
const url = 'https://YOUR-REGION-PROJECT.cloudfunctions.net/trigger-dag-function';
const data = {
    bucket: 'my-data-bucket',
    file: 'data/input/dataset.csv'
};

fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📚 API Reference

### Endpoint
```
POST https://YOUR-REGION-PROJECT.cloudfunctions.net/trigger-dag-function
GET  https://YOUR-REGION-PROJECT.cloudfunctions.net/trigger-dag-function
```

### Request Parameters

#### POST Request Body (JSON)
```json
{
  "bucket": "string",     // GCS bucket name
  "file": "string",       // File path in bucket
  "dag_id": "string",     // Optional: Override default DAG ID
  "additional_config": {} // Optional: Additional DAG configuration
}
```

#### GET Request Query Parameters
```
?bucket=string&file=string&dag_id=string
```

### Response Format

#### Success Response
```json
{
  "status": "success",
  "message": "DAG triggered successfully",
  "dag_id": "gcs_dataflow_bigquery_official",
  "dag_conf": {
    "bucket": "my-bucket",
    "file": "data/input/file.csv"
  },
  "response": "Airflow response details"
}
```

#### Error Response
```json
{
  "status": "error",
  "message": "Failed to trigger DAG: Permission denied"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - DAG triggered successfully |
| 400 | Bad Request - Invalid parameters |
| 403 | Forbidden - Authentication/authorization failed |
| 500 | Internal Server Error - Function execution failed |

## 📊 Monitoring

### Cloud Function Metrics
Monitor your function performance in the Google Cloud Console:

1. **Go to Cloud Functions**
2. **Select your function**
3. **View metrics**:
   - Invocations
   - Duration
   - Memory usage
   - Errors

### Logging
View function logs:
```bash
# View recent logs
gcloud functions logs read trigger-dag-function --limit 50

# Stream logs in real-time
gcloud functions logs tail trigger-dag-function
```

### Airflow Monitoring
Monitor DAG execution in Airflow UI:
1. Access Composer environment
2. Open Airflow web interface
3. Check DAG runs and task status

## 🐛 Troubleshooting

### Common Issues

#### 1. Function Deployment Fails
**Error:** `The user-provided container failed to start`

**Solutions:**
- Check `requirements.txt` for correct dependencies
- Verify Python syntax in `main.py`
- Ensure entry point function name matches deployment command

#### 2. Permission Denied (403)
**Error:** `You do not have permission to perform this operation`

**Solutions:**
- Grant `roles/composer.user` to the function's service account
- Check Airflow RBAC configuration
- Verify IAM policies

#### 3. Connection Timeout
**Error:** `Connection timeout to Composer`

**Solutions:**
- Verify Composer web server URL
- Check network connectivity
- Increase function timeout setting

#### 4. DAG Not Found
**Error:** `DAG 'your-dag-id' not found`

**Solutions:**
- Verify DAG ID spelling
- Check if DAG is deployed in Composer
- Ensure DAG is not paused

### Debug Mode
Enable debug logging by setting environment variable:
```bash
gcloud functions deploy trigger-dag-function \
    --set-env-vars DEBUG=true
```

### Health Check
Test function health:
```bash
curl -X GET https://YOUR-REGION-PROJECT.cloudfunctions.net/trigger-dag-function/health
```
