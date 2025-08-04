"""
RESTful API controller for prompt management.
Provides JSON API endpoints following REST conventions.
"""
from flask import Blueprint, jsonify, request
from app.services import PromptService, TagService, MergeService, CursorService, AttachedPromptService
from app.controllers.base import BaseController
from functools import wraps


# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
prompt_service = PromptService()
tag_service = TagService()
merge_service = MergeService()
cursor_service = CursorService()

# Initialize repositories for AttachedPromptService
from app.repositories import AttachedPromptRepository, PromptRepository
attached_prompt_repo = AttachedPromptRepository()
prompt_repo = PromptRepository()
attached_prompt_service = AttachedPromptService(attached_prompt_repo, prompt_repo)


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
    attachment_stats = prompt_service.get_prompt_attachment_statistics()
    
    return jsonify({
        'prompts': prompt_stats,
        'tags': tag_stats,
        'attachments': attachment_stats
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


# Attached Prompts endpoints
@api_bp.route('/prompts/<int:prompt_id>/attached', methods=['GET'])
@BaseController.handle_service_error
def get_attached_prompts(prompt_id):
    """
    Get all prompts attached to the specified prompt.
    
    Returns:
        JSON response with attached prompts data
    """
    try:
        attached_prompts = attached_prompt_service.get_attached_prompts_with_details(prompt_id)
        
        return jsonify({
            'success': True,
            'data': attached_prompts,
            'count': len(attached_prompts)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/prompts/<int:prompt_id>/attach', methods=['POST'])
@require_json
@BaseController.validate_request_data(['attached_prompt_id'])
@BaseController.handle_service_error
def attach_prompt(prompt_id):
    """
    Attach a prompt to the specified prompt.
    
    Required fields:
    - attached_prompt_id: ID of the prompt to attach
    
    Returns:
        JSON response with created attachment data
    """
    try:
        data = request.get_json()
        attached_id = data['attached_prompt_id']
        
        # Validate input
        if not isinstance(attached_id, int):
            return jsonify({
                'success': False,
                'error': 'attached_prompt_id must be an integer'
            }), 400
        
        # Create attachment
        attached_prompt = attached_prompt_service.attach_prompt(prompt_id, attached_id)
        
        return jsonify({
            'success': True,
            'data': attached_prompt.to_dict(),
            'message': f'Prompt {attached_id} successfully attached to prompt {prompt_id}'
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/prompts/<int:prompt_id>/attach/<int:attached_id>', methods=['DELETE'])
@BaseController.handle_service_error
def detach_prompt(prompt_id, attached_id):
    """
    Detach a prompt from the specified prompt.
    
    Returns:
        JSON response with operation result
    """
    try:
        success = attached_prompt_service.detach_prompt(prompt_id, attached_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Prompt {attached_id} successfully detached from prompt {prompt_id}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Attachment between prompt {prompt_id} and {attached_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/prompts/<int:prompt_id>/attached/reorder', methods=['PUT'])
@require_json
@BaseController.validate_request_data(['order_data'])
@BaseController.handle_service_error
def reorder_attached_prompts(prompt_id):
    """
    Reorder attached prompts for a main prompt.
    
    Required fields:
    - order_data: List of dictionaries with 'attached_prompt_id' and 'order' keys
    
    Example:
    {
        "order_data": [
            {"attached_prompt_id": 1, "order": 0},
            {"attached_prompt_id": 2, "order": 1}
        ]
    }
    
    Returns:
        JSON response with operation result
    """
    try:
        data = request.get_json()
        order_data = data['order_data']
        
        # Validate order_data structure
        if not isinstance(order_data, list):
            return jsonify({
                'success': False,
                'error': 'order_data must be a list'
            }), 400
        
        for item in order_data:
            if not isinstance(item, dict) or 'attached_prompt_id' not in item or 'order' not in item:
                return jsonify({
                    'success': False,
                    'error': 'Each item in order_data must contain attached_prompt_id and order'
                }), 400
        
        # Reorder attachments
        success = attached_prompt_service.reorder_attachments(prompt_id, order_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Attached prompts reordered successfully for prompt {prompt_id}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reorder attached prompts'
            }), 500
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/prompts/<int:prompt_id>/attached/available', methods=['GET'])
@BaseController.handle_service_error
def get_available_for_attachment(prompt_id):
    """
    Get prompts that can be attached to the specified prompt.
    
    Query parameters:
    - exclude_ids: Comma-separated list of prompt IDs to exclude
    
    Returns:
        JSON response with available prompts
    """
    try:
        exclude_ids_param = request.args.get('exclude_ids', '')
        exclude_ids = None
        
        if exclude_ids_param:
            try:
                exclude_ids = [int(id.strip()) for id in exclude_ids_param.split(',') if id.strip()]
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'exclude_ids must be comma-separated integers'
                }), 400
        
        available_prompts = attached_prompt_service.get_available_for_attachment(prompt_id, exclude_ids)
        
        return jsonify({
            'success': True,
            'data': [prompt.to_dict() for prompt in available_prompts],
            'count': len(available_prompts)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/prompts/combinations/popular', methods=['GET'])
@BaseController.handle_service_error
def get_popular_combinations():
    """
    Get most frequently used prompt combinations.
    
    Query parameters:
    - limit: Maximum number of combinations to return (default: 10, max: 50)
    
    Returns:
        JSON response with popular combinations data
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Validate limit
        if limit < 1 or limit > 50:
            return jsonify({
                'success': False,
                'error': 'limit must be between 1 and 50'
            }), 400
        
        combinations = attached_prompt_service.get_popular_combinations(limit)
        
        return jsonify({
            'success': True,
            'data': combinations,
            'count': len(combinations)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/prompts/<int:prompt_id>/attached/validate', methods=['POST'])
@require_json
@BaseController.validate_request_data(['attached_prompt_id'])
@BaseController.handle_service_error
def validate_attachment(prompt_id):
    """
    Validate if an attachment would be valid without creating it.
    
    Required fields:
    - attached_prompt_id: ID of the prompt to validate for attachment
    
    Returns:
        JSON response with validation result
    """
    try:
        data = request.get_json()
        attached_id = data['attached_prompt_id']
        
        # Validate input
        if not isinstance(attached_id, int):
            return jsonify({
                'success': False,
                'error': 'attached_prompt_id must be an integer'
            }), 400
        
        # Validate attachment
        errors = attached_prompt_service.validate_attachment(prompt_id, attached_id)
        
        if errors:
            return jsonify({
                'success': False,
                'valid': False,
                'errors': errors
            }), 400
        else:
            return jsonify({
                'success': True,
                'valid': True,
                'message': 'Attachment is valid'
            }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/prompts/attachments/statistics', methods=['GET'])
@BaseController.handle_service_error
def get_attachment_statistics():
    """
    Get statistics about prompt attachments.
    
    Returns:
        JSON response with attachment statistics
    """
    try:
        stats = prompt_service.get_prompt_attachment_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/prompts/<int:main_id>/attach/<int:attached_id>/use', methods=['POST'])
@BaseController.handle_service_error
def increment_attachment_usage(main_id, attached_id):
    """
    Increment usage count for a specific attachment.
    
    Returns:
        JSON response with operation result
    """
    try:
        success = attached_prompt_service.increment_usage(main_id, attached_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Usage count incremented for attachment {main_id} -> {attached_id}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Attachment {main_id} -> {attached_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500