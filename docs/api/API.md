# API Documentation

## Base URL
```
http://localhost:5001/api
```

## Response Format
All API responses follow a consistent JSON structure:

### Success Response
```json
{
  "data": {},
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": {} // Optional additional error information
}
```

## Authentication
Currently, the API does not require authentication. This will be added in future versions.

## Endpoints

### Prompts

#### List Prompts
```http
GET /api/prompts
```

**Query Parameters:**
- `page` (integer): Page number, default: 1
- `per_page` (integer): Items per page, default: 20, max: 100
- `search` (string): Search in title, content, description
- `tags` (string): Comma-separated tag names
- `is_active` (boolean): Filter by active status
- `sort_by` (string): Sort field (created, updated, title)
- `sort_order` (string): Sort order (asc, desc)

**Response:**
```json
{
  "prompts": [
    {
      "id": 1,
      "title": "Python Code Review",
      "content": "Please review the following Python code...",
      "description": "A prompt for code reviews",
      "is_active": true,
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z",
      "tags": [
        {
          "id": 1,
          "name": "python",
          "color": "#3776AB"
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Single Prompt
```http
GET /api/prompts/{id}
```

**Response:**
```json
{
  "prompt": {
    "id": 1,
    "title": "Python Code Review",
    "content": "Please review the following Python code...",
    "description": "A prompt for code reviews",
    "is_active": true,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z",
    "tags": [...]
  }
}
```

#### Create Prompt
```http
POST /api/prompts
```

**Request Body:**
```json
{
  "title": "New Prompt",
  "content": "This is the prompt content",
  "description": "Optional description",
  "tags": ["python", "api"],
  "is_active": true
}
```

**Required Fields:**
- `title` (string): Prompt title, max 255 characters
- `content` (string): Prompt content

**Response:** 201 Created
```json
{
  "message": "Prompt created successfully",
  "prompt": {
    "id": 2,
    "title": "New Prompt",
    ...
  }
}
```

#### Update Prompt
```http
PUT /api/prompts/{id}
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "description": "Updated description",
  "tags": ["python", "updated"],
  "is_active": true
}
```

**Note:** All fields are optional. Only provided fields will be updated.

**Response:** 200 OK
```json
{
  "message": "Prompt updated successfully",
  "prompt": {...}
}
```

#### Delete Prompt
```http
DELETE /api/prompts/{id}
```

**Query Parameters:**
- `hard` (boolean): If true, permanently delete; otherwise soft delete (default: false)

**Response:** 200 OK
```json
{
  "message": "Prompt deleted successfully"
}
```

#### Restore Prompt
```http
POST /api/prompts/{id}/restore
```

**Response:** 200 OK
```json
{
  "message": "Prompt restored successfully"
}
```

#### Duplicate Prompt
```http
POST /api/prompts/{id}/duplicate
```

**Request Body (Optional):**
```json
{
  "title": "Copy of Original"
}
```

**Response:** 201 Created
```json
{
  "message": "Prompt duplicated successfully",
  "prompt": {...}
}
```

#### Merge Prompts
```http
POST /api/prompts/merge
```

**Request Body:**
```json
{
  "prompt_ids": [1, 2, 3],
  "strategy": "simple",
  "options": {
    "include_title": true,
    "include_description": false,
    "separator": "\n---\n",
    "template": "Custom template with {variables}"
  }
}
```

**Strategies:**
- `simple`: Simple concatenation
- `separator`: With custom separator
- `numbered`: Numbered list
- `bulleted`: Bullet points
- `template`: Custom template

**Response:** 200 OK
```json
{
  "message": "Prompts merged successfully",
  "merged_content": "...",
  "metadata": {
    "strategy": "simple",
    "prompt_count": 3,
    "prompt_ids": [1, 2, 3],
    "merged_at": "2023-12-01T10:00:00Z"
  }
}
```

#### Search Prompts
```http
GET /api/prompts/search
```

**Query Parameters:**
- `q` (string, required): Search query
- `include_inactive` (boolean): Include inactive prompts (default: false)

**Response:** 200 OK
```json
{
  "query": "python",
  "count": 5,
  "prompts": [...]
}
```

### Tags

#### List Tags
```http
GET /api/tags
```

**Query Parameters:**
- `popular` (boolean): Return popular tags with usage count
- `limit` (integer): Limit results (for popular tags)

**Response:**
```json
{
  "tags": [
    {
      "id": 1,
      "name": "python",
      "color": "#3776AB",
      "created_at": "2023-12-01T10:00:00Z",
      "prompt_count": 15  // Only if popular=true
    }
  ]
}
```

#### Get Single Tag
```http
GET /api/tags/{id}
```

**Response:**
```json
{
  "tag": {
    "id": 1,
    "name": "python",
    "color": "#3776AB",
    "created_at": "2023-12-01T10:00:00Z",
    "prompt_count": 15
  }
}
```

#### Create Tag
```http
POST /api/tags
```

**Request Body:**
```json
{
  "name": "New Tag",
  "color": "#FF5733"
}
```

**Required Fields:**
- `name` (string): Tag name, will be normalized

**Response:** 201 Created
```json
{
  "message": "Tag created successfully",
  "tag": {...}
}
```

#### Update Tag
```http
PUT /api/tags/{id}
```

**Request Body:**
```json
{
  "name": "Updated Tag",
  "color": "#00FF00"
}
```

**Response:** 200 OK
```json
{
  "message": "Tag updated successfully",
  "tag": {...}
}
```

#### Delete Tag
```http
DELETE /api/tags/{id}
```

**Query Parameters:**
- `reassign_to` (integer): Tag ID to reassign prompts to

**Response:** 200 OK
```json
{
  "message": "Tag deleted successfully"
}
```

#### Merge Tags
```http
POST /api/tags/merge
```

**Request Body:**
```json
{
  "source_id": 1,
  "target_id": 2
}
```

**Response:** 200 OK
```json
{
  "message": "Tags merged successfully",
  "tag": {...}  // Target tag
}
```

#### Tag Statistics
```http
GET /api/tags/statistics
```

**Response:**
```json
{
  "statistics": {
    "total_tags": 25,
    "used_tags": 20,
    "unused_tags": 5,
    "avg_prompts_per_tag": 3.5,
    "max_prompts_per_tag": 15,
    "min_prompts_per_tag": 0,
    "popular_tags": [
      {
        "name": "python",
        "count": 15
      }
    ]
  }
}
```

### General

#### Statistics
```http
GET /api/statistics
```

**Response:**
```json
{
  "prompts": {
    "total_prompts": 100,
    "active_prompts": 95,
    "inactive_prompts": 5,
    "active_percentage": 95.0
  },
  "tags": {
    "total_tags": 25,
    "used_tags": 20,
    "unused_tags": 5,
    ...
  }
}
```

#### Health Check
```http
GET /api/health
```

**Response:** 200 OK
```json
{
  "status": "healthy",
  "service": "Prompt Manager API",
  "version": "1.0.0"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request - Invalid input |
| 404  | Not Found - Resource doesn't exist |
| 500  | Internal Server Error |

## Rate Limiting
Currently not implemented. Will be added in future versions.

## Examples

### Python
```python
import requests

# Base URL
BASE_URL = "http://localhost:5001/api"

# Create a prompt
response = requests.post(f"{BASE_URL}/prompts", json={
    "title": "Python Best Practices",
    "content": "What are the best practices for Python development?",
    "tags": ["python", "best-practices"]
})
prompt = response.json()

# Search prompts
response = requests.get(f"{BASE_URL}/prompts/search", params={"q": "python"})
results = response.json()

# Merge prompts
response = requests.post(f"{BASE_URL}/prompts/merge", json={
    "prompt_ids": [1, 2, 3],
    "strategy": "numbered"
})
merged = response.json()
```

### JavaScript
```javascript
// Base URL
const BASE_URL = "http://localhost:5001/api";

// Create a prompt
fetch(`${BASE_URL}/prompts`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: "JavaScript Tips",
    content: "Share your best JavaScript tips",
    tags: ["javascript", "tips"]
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Get prompts with pagination
fetch(`${BASE_URL}/prompts?page=2&per_page=10`)
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL
```bash
# Create a prompt
curl -X POST http://localhost:5001/api/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "API Testing",
    "content": "How to test REST APIs effectively",
    "tags": ["api", "testing"]
  }'

# Search prompts
curl "http://localhost:5001/api/prompts/search?q=testing"

# Delete a tag
curl -X DELETE http://localhost:5001/api/tags/5
```