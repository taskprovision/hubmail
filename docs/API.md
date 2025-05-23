# DocPro - API Reference

## Service Endpoints

### Elasticsearch (Port: 9200)

#### Search Documents
```bash
GET /documents/_search
```
**Example:**
```bash
curl "http://localhost:9200/documents/_search?q=invoice&size=10"
```

#### Get Document by ID
```bash
GET /documents/_doc/{id}
```
**Example:**
```bash
curl "http://localhost:9200/documents/_doc/ABC123"
```

#### Index New Document
```bash
POST /documents/_doc
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:9200/documents/_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "invoice-001.pdf",
    "document_type": "INVOICE",
    "extracted_text": "Invoice content...",
    "processing_timestamp": "2024-01-20T10:30:00Z"
  }'
```

#### Search with Query
```bash
POST /documents/_search
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:9200/documents/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"match": {"document_type": "INVOICE"}},
          {"range": {"analysis_results.total_amount": {"gte": 1000}}}
        ]
      }
    },
    "sort": [{"processing_timestamp": {"order": "desc"}}]
  }'
```

### Apache Tika (Port: 9998)

#### Extract Text
```bash
PUT /tika
Content-Type: application/octet-stream
```
**Example:**
```bash
curl -T document.pdf "http://localhost:9998/tika"
```

#### Extract Metadata
```bash
PUT /meta
Content-Type: application/octet-stream
```
**Example:**
```bash
curl -T document.pdf "http://localhost:9998/meta"
```

#### Detect MIME Type
```bash
PUT /detect
Content-Type: application/octet-stream
```
**Example:**
```bash
curl -T document.pdf "http://localhost:9998/detect"
```

### Ollama AI (Port: 11437)

#### List Available Models
```bash
GET /api/tags
```
**Example:**
```bash
curl "http://localhost:11437/api/tags"
```

#### Generate Analysis
```bash
POST /api/generate
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:11437/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2:13b",
    "prompt": "Analyze this invoice document: Invoice #123, Amount: $5000, Date: 2024-01-20. Extract key information in JSON format.",
    "stream": false
  }'
```

#### Pull Model
```bash
POST /api/pull
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:11437/api/pull" \
  -H "Content-Type: application/json" \
  -d '{"name": "llama2:7b"}'
```

### MinIO Storage (Port: 9000)

#### List Buckets
```bash
GET /
Authorization: AWS4-HMAC-SHA256 ...
```
**Example with AWS CLI:**
```bash
aws s3 ls --endpoint-url http://localhost:9000
```

#### Upload Document
```bash
PUT /{bucket}/{key}
```
**Example:**
```bash
aws s3 cp document.pdf s3://documents/ --endpoint-url http://localhost:9000
```

#### Download Document
```bash
GET /{bucket}/{key}
```
**Example:**
```bash
aws s3 cp s3://documents/document.pdf . --endpoint-url http://localhost:9000
```

### Node-RED (Port: 1880)

#### Get All Flows
```bash
GET /flows
```
**Example:**
```bash
curl "http://localhost:1880/flows"
```

#### Deploy Flows
```bash
POST /flows
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:1880/flows" \
  -H "Content-Type: application/json" \
  -d @flows.json
```

#### Trigger Inject Node
```bash
POST /inject/{node-id}
```
**Example:**
```bash
curl -X POST "http://localhost:1880/inject/node-12345"
```

## Custom API Endpoints

### Document Processing

#### Upload and Process
```bash
POST /api/process-document
Content-Type: multipart/form-data
```
**Example:**
```bash
curl -X POST "http://localhost:1880/api/process-document" \
  -F "file=@document.pdf" \
  -F "type=INVOICE"
```

#### Get Processing Status
```bash
GET /api/status/{job-id}
```
**Example:**
```bash
curl "http://localhost:1880/api/status/job-abc123"
```

### Analytics

#### Get Document Statistics
```bash
GET /api/stats/documents
```
**Example:**
```bash
curl "http://localhost:1880/api/stats/documents?period=7d"
```

#### Get Compliance Report
```bash
GET /api/compliance/report
```
**Example:**
```bash
curl "http://localhost:1880/api/compliance/report?type=COR&from=2024-01-01"
```

## Response Formats

### Document Object
```json
{
  "id": "doc-12345",
  "filename": "invoice-001.pdf",
  "document_type": "INVOICE",
  "file_size": 1024576,
  "processing_timestamp": "2024-01-20T10:30:00Z",
  "extracted_text": "Invoice content...",
  "analysis_results": {
    "invoice_number": "INV-001",
    "total_amount": 5000.00,
    "currency": "USD",
    "confidence_score": 0.95
  },
  "compliance_status": "COMPLIANT"
}
```

### Error Response
```json
{
  "error": {
    "code": "PROCESSING_FAILED",
    "message": "Document parsing failed",
    "details": "Unsupported file format",
    "timestamp": "2024-01-20T10:30:00Z"
  }
}
```

### Search Response
```json
{
  "took": 5,
  "total": {
    "value": 150,
    "relation": "eq"
  },
  "hits": [
    {
      "_id": "doc-12345",
      "_source": {
        "filename": "invoice-001.pdf",
        "document_type": "INVOICE"
      }
    }
  ]
}
```

## Authentication

### MinIO S3 API
```bash
# Using AWS CLI with credentials
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin123
export AWS_DEFAULT_REGION=us-east-1
```

### Node-RED Admin API
```bash
# Basic authentication if enabled
curl -u "admin:password" "http://localhost:1880/flows"
```

## Rate Limits

- **Elasticsearch**: 1000 requests/minute per IP
- **Tika**: 100 documents/minute
- **Ollama**: 10 generations/minute
- **Node-RED**: No default limits

## Error Codes

| Code | Service | Description |
|------|---------|-------------|
| 400 | All | Bad Request |
| 401 | MinIO/Node-RED | Unauthorized |
| 404 | Elasticsearch | Document not found |
| 413 | Tika | Document too large |
| 429 | All | Rate limit exceeded |
| 500 | All | Internal server error |
| 503 | Ollama | Model not loaded |