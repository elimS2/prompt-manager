"""
RESTful API controller for prompt management.
Provides JSON API endpoints following REST conventions.
"""
from flask import Blueprint, jsonify, request
from app.services import PromptService, TagService, MergeService, CursorService
from app.controllers.base import BaseController
from functools import wraps


# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
prompt_service = PromptService()
tag_service = TagService()
merge_service = MergeService()
cursor_service = CursorService()


def require_json(f):
    """Decorator to ensure request has JSON content."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function


# Prompt endpoints
@api_bp.route('/prompts', methods=['GET'])
def get_prompts():
    """
    Get prompts with filtering and pagination.
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    - search: Search query
    - tags: Comma-separated tag names
    - is_active: Filter by active status (true/false)
    - sort_by: Sort field (created, updated, title)
    - sort_order: Sort order (asc, desc)
    """
    # Get filter parameters
    filters = BaseController.get_filter_params()
    
    # Get pagination parameters
    pagination = BaseController.get_pagination_params()
    filters.update(pagination)
    
    # Get prompts
    result = prompt_service.get_prompts_by_filters(filters)
    
    # Format response
    response = {
        'prompts': [prompt.to_dict() for prompt in result.get('items', [])],
        'pagination': {
            'page': result.get('page', 1),
            'per_page': result.get('per_page', 20),
            'total': result.get('total', 0),
            'total_pages': result.get('total_pages', 0),
            'has_next': result.get('has_next', False),
            'has_prev': result.get('has_prev', False)
        }
    }
    
    return jsonify(response), 200


@api_bp.route('/prompts/<int:id>', methods=['GET'])
def get_prompt(id):
    """Get a single prompt by ID."""
    prompt = prompt_service.get_prompt(id)
    
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    return jsonify({'prompt': prompt.to_dict()}), 200


@api_bp.route('/prompts', methods=['POST'])
@require_json
@BaseController.validate_request_data(['title', 'content'])
@BaseController.handle_service_error
def create_prompt():
    """
    Create a new prompt.
    
    Required fields:
    - title: Prompt title
    - content: Prompt content
    
    Optional fields:
    - description: Prompt description
    - tags: List of tag names
    - is_active: Active status (default: true)
    """
    data = request.get_json()
    
    # Create prompt
    prompt = prompt_service.create_prompt(data)
    
    return jsonify({
        'message': 'Prompt created successfully',
        'prompt': prompt.to_dict()
    }), 201


@api_bp.route('/prompts/<int:id>', methods=['PUT'])
@require_json
@BaseController.handle_service_error
def update_prompt(id):
    """
    Update an existing prompt.
    
    All fields are optional:
    - title: New title
    - content: New content
    - description: New description
    - tags: New list of tag names (replaces existing)
    - is_active: New active status
    """
    data = request.get_json()
    
    # Update prompt
    prompt = prompt_service.update_prompt(id, data)
    
    return jsonify({
        'message': 'Prompt updated successfully',
        'prompt': prompt.to_dict()
    }), 200


@api_bp.route('/prompts/<int:id>', methods=['DELETE'])
def delete_prompt(id):
    """
    Delete a prompt.
    
    Query parameters:
    - hard: If true, permanently delete; otherwise soft delete (default: false)
    """
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    
    success = prompt_service.delete_prompt(id, soft=not hard_delete)
    
    if success:
        return jsonify({'message': 'Prompt deleted successfully'}), 200
    else:
        return jsonify({'error': 'Prompt not found'}), 404


@api_bp.route('/prompts/<int:id>/restore', methods=['POST'])
def restore_prompt(id):
    """Restore a soft-deleted prompt."""
    success = prompt_service.restore_prompt(id)
    
    if success:
        return jsonify({'message': 'Prompt restored successfully'}), 200
    else:
        return jsonify({'error': 'Prompt not found or not deleted'}), 404


@api_bp.route('/prompts/<int:id>/duplicate', methods=['POST'])
@BaseController.handle_service_error
def duplicate_prompt(id):
    """
    Duplicate a prompt.
    
    Optional fields:
    - title: New title for the duplicate
    """
    data = request.get_json() or {}
    new_title = data.get('title')
    
    new_prompt = prompt_service.duplicate_prompt(id, new_title)
    
    return jsonify({
        'message': 'Prompt duplicated successfully',
        'prompt': new_prompt.to_dict()
    }), 201


@api_bp.route('/prompts/merge', methods=['POST'])
@require_json
@BaseController.validate_request_data(['prompt_ids'])
@BaseController.handle_service_error
def merge_prompts():
    """
    Merge multiple prompts.
    
    Required fields:
    - prompt_ids: List of prompt IDs to merge
    
    Optional fields:
    - strategy: Merge strategy (simple, separator, numbered, bulleted, template)
    - options: Strategy-specific options
    """
    data = request.get_json()
    
    prompt_ids = data['prompt_ids']
    strategy = data.get('strategy', 'simple')
    options = data.get('options', {})
    
    # Validate merge
    validation = merge_service.validate_merge(prompt_ids)
    if not validation['valid']:
        return jsonify({
            'error': 'Validation failed',
            'errors': validation['errors'],
            'warnings': validation['warnings']
        }), 400
    
    # Perform merge
    result = merge_service.merge_prompts(prompt_ids, strategy, options)
    
    return jsonify({
        'message': 'Prompts merged successfully',
        'merged_content': result['merged_content'],
        'metadata': result['metadata'],
        'warnings': validation['warnings']
    }), 200


@api_bp.route('/prompts/search', methods=['GET'])
def search_prompts():
    """
    Search prompts.
    
    Query parameters:
    - q: Search query (required)
    - include_inactive: Include inactive prompts (default: false)
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    prompts = prompt_service.search_prompts(query, include_inactive)
    
    return jsonify({
        'query': query,
        'count': len(prompts),
        'prompts': [prompt.to_dict() for prompt in prompts]
    }), 200


# Tag endpoints
@api_bp.route('/tags', methods=['GET'])
def get_tags():
    """
    Get all tags.
    
    Query parameters:
    - popular: If true, return popular tags with usage count
    - limit: Limit number of results (for popular tags)
    """
    if request.args.get('popular', 'false').lower() == 'true':
        limit = request.args.get('limit', 10, type=int)
        popular_tags = tag_service.get_popular_tags(limit)
        
        return jsonify({
            'tags': [
                {
                    'id': item['tag'].id,
                    'name': item['tag'].name,
                    'color': item['tag'].color,
                    'usage_count': item['usage_count']
                }
                for item in popular_tags
            ]
        }), 200
    else:
        # Get all tags
        from app.repositories import TagRepository
        tag_repo = TagRepository()
        tags = tag_repo.get_all()
        
        return jsonify({
            'tags': [tag.to_dict() for tag in tags]
        }), 200


@api_bp.route('/tags/<int:id>', methods=['GET'])
def get_tag(id):
    """Get a single tag by ID."""
    from app.repositories import TagRepository
    tag_repo = TagRepository()
    tag = tag_repo.get_by_id(id)
    
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    return jsonify({'tag': tag.to_dict()}), 200


@api_bp.route('/tags', methods=['POST'])
@require_json
@BaseController.validate_request_data(['name'])
@BaseController.handle_service_error
def create_tag():
    """
    Create a new tag.
    
    Required fields:
    - name: Tag name
    
    Optional fields:
    - color: Hex color code (e.g., #FF5733)
    """
    data = request.get_json()
    
    tag = tag_service.create_tag(data['name'], data.get('color'))
    
    return jsonify({
        'message': 'Tag created successfully',
        'tag': tag.to_dict()
    }), 201


@api_bp.route('/tags/<int:id>', methods=['PUT'])
@require_json
@BaseController.handle_service_error
def update_tag(id):
    """
    Update a tag.
    
    Optional fields:
    - name: New tag name
    - color: New hex color code
    """
    data = request.get_json()
    
    tag = tag_service.update_tag(id, data.get('name'), data.get('color'))
    
    return jsonify({
        'message': 'Tag updated successfully',
        'tag': tag.to_dict()
    }), 200


@api_bp.route('/tags/<int:id>', methods=['DELETE'])
def delete_tag(id):
    """
    Delete a tag.
    
    Query parameters:
    - reassign_to: Tag ID to reassign prompts to
    """
    reassign_to = request.args.get('reassign_to', type=int)
    
    try:
        success = tag_service.delete_tag(id, reassign_to)
        
        if success:
            return jsonify({'message': 'Tag deleted successfully'}), 200
        else:
            return jsonify({'error': 'Tag not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/tags/merge', methods=['POST'])
@require_json
@BaseController.validate_request_data(['source_id', 'target_id'])
@BaseController.handle_service_error
def merge_tags():
    """
    Merge one tag into another.
    
    Required fields:
    - source_id: ID of tag to be merged
    - target_id: ID of tag to merge into
    """
    data = request.get_json()
    
    tag = tag_service.merge_tags(data['source_id'], data['target_id'])
    
    return jsonify({
        'message': 'Tags merged successfully',
        'tag': tag.to_dict()
    }), 200


@api_bp.route('/tags/statistics', methods=['GET'])
def tag_statistics():
    """Get tag usage statistics."""
    stats = tag_service.get_tag_statistics()
    
    return jsonify({'statistics': stats}), 200


# General endpoints
@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get overall application statistics."""
    prompt_stats = prompt_service.get_prompt_statistics()
    tag_stats = tag_service.get_tag_statistics()
    
    return jsonify({
        'prompts': prompt_stats,
        'tags': tag_stats
    }), 200


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Prompt Manager API',
        'version': '1.0.0'
    }), 200


# Cursor IDE Integration endpoints
@api_bp.route('/cursor/status', methods=['GET'])
def cursor_status():
    """Get Cursor IDE status and capabilities."""
    status = cursor_service.get_cursor_status()
    
    return jsonify(status), 200


@api_bp.route('/cursor/send', methods=['POST'])
@require_json
@BaseController.validate_request_data(['content'])
@BaseController.handle_service_error
def send_to_cursor():
    """
    Send prompt content to Cursor IDE.
    
    Required fields:
    - content: The prompt content to send
    
    Optional fields:
    - title: Optional title for the prompt
    - method: 'clipboard' or 'file' (default: 'clipboard')
    """
    data = request.get_json()
    content = data['content']
    title = data.get('title')
    method = data.get('method', 'clipboard')
    
    if method == 'clipboard':
        result = cursor_service.copy_to_clipboard_with_instructions(content, title)
    else:
        result = cursor_service.send_prompt_to_cursor(content, title)
    
    return jsonify(result), 200 if result['success'] else 400


@api_bp.route('/cursor/send/<int:prompt_id>', methods=['POST'])
@BaseController.handle_service_error
def send_prompt_to_cursor(prompt_id):
    """
    Send a specific prompt to Cursor IDE.
    
    Query parameters:
    - method: 'clipboard' or 'file' (default: 'clipboard')
    """
    # Get the prompt
    prompt = prompt_service.get_prompt(prompt_id)
    
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    method = request.args.get('method', 'clipboard')
    
    if method == 'clipboard':
        result = cursor_service.copy_to_clipboard_with_instructions(prompt.content, prompt.title)
    else:
        result = cursor_service.send_prompt_to_cursor(prompt.content, prompt.title)
    
    return jsonify(result), 200 if result['success'] else 400