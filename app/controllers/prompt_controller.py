"""
Web controller for prompt management.
Handles HTTP requests for the web interface.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import PromptService, TagService, MergeService
from app.controllers.base import BaseController
import re


# Create blueprint
prompt_bp = Blueprint('prompt', __name__)

# Initialize services
prompt_service = PromptService()
tag_service = TagService()
merge_service = MergeService()


def highlight_search(text, query):
    """Highlight search query in text."""
    if not text or not query:
        return text
    
    # Escape special regex characters
    escaped_query = re.escape(query)
    # Create regex pattern for case-insensitive matching
    pattern = re.compile(f'({escaped_query})', re.IGNORECASE)
    
    # Replace matches with highlighted version
    highlighted = pattern.sub(r'<mark class="search-highlight">\1</mark>', str(text))
    return highlighted


# Register template filter
def register_filters(app):
    """Register template filters."""
    app.jinja_env.filters['highlight_search'] = highlight_search


@prompt_bp.route('/')
@prompt_bp.route('/prompts')
def index():
    """Display list of prompts with filtering and pagination."""
    # Get pagination parameters
    pagination_params = BaseController.get_pagination_params()
    
    # Get filter parameters
    filters = BaseController.get_filter_params()
    filters.update(pagination_params)
    
    # Get prompts
    result = prompt_service.get_prompts_by_filters(filters)
    
    # Get popular tags for sidebar
    popular_tags = tag_service.get_popular_tags(limit=10)
    
    # Handle result format (list or dict with pagination)
    if isinstance(result, dict):
        prompts = result.get('items', [])
        pagination = result
    else:
        prompts = result
        pagination = None
    
    return render_template('prompt/list.html',
                         prompts=prompts,
                         pagination=pagination,
                         filters=filters,
                         popular_tags=popular_tags)


@prompt_bp.route('/prompts/create', methods=['GET', 'POST'])
@BaseController.handle_service_error
def create():
    """Create a new prompt."""
    if request.method == 'POST':
        try:
            # Validate required fields
            data = BaseController.get_request_data()
            
            # Basic validation
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            
            if not title:
                flash('Title is required', 'error')
                return redirect(url_for('prompt.create'))
            
            if not content:
                flash('Content is required', 'error')
                return redirect(url_for('prompt.create'))
            
            # Process tags
            tag_names = request.form.get('tags', '').split(',')
            tag_names = [tag.strip() for tag in tag_names if tag.strip()]
            data['tags'] = tag_names
            
            # Handle checkbox for is_active
            is_active = request.form.get('is_active')
            if is_active == 'true':
                data['is_active'] = True
            else:
                data['is_active'] = False
            
            # Create prompt
            prompt = prompt_service.create_prompt(data)
            
            flash('Prompt created successfully!', 'success')
            return redirect(url_for('prompt.view', id=prompt.id))
            
        except Exception as e:
            # Show user-friendly error
            flash(f'Failed to create prompt: {str(e)}', 'error')
            return redirect(url_for('prompt.create'))
    
    # GET request - show form
    return render_template('prompt/create.html')


@prompt_bp.route('/prompts/<int:id>')
def view(id):
    """View a single prompt."""
    prompt = prompt_service.get_prompt(id)
    
    if not prompt:
        flash('Prompt not found', 'error')
        return redirect(url_for('prompt.index'))
    
    # Get suggested tags
    suggested_tags = tag_service.suggest_tags(prompt.content, limit=5)
    
    return render_template('prompt/view.html',
                         prompt=prompt,
                         suggested_tags=suggested_tags)


@prompt_bp.route('/prompts/<int:id>/edit', methods=['GET', 'POST'])
@BaseController.handle_service_error
def edit(id):
    """Edit an existing prompt."""
    prompt = prompt_service.get_prompt(id)
    
    if not prompt:
        flash('Prompt not found', 'error')
        return redirect(url_for('prompt.index'))
    
    if request.method == 'POST':
        # Get update data
        data = BaseController.get_request_data()
        
        # Process tags
        if 'tags' in request.form:
            tag_names = request.form.get('tags', '').split(',')
            tag_names = [tag.strip() for tag in tag_names if tag.strip()]
            data['tags'] = tag_names
        
        # Update prompt
        prompt = prompt_service.update_prompt(id, data)
        
        flash('Prompt updated successfully!', 'success')
        return redirect(url_for('prompt.view', id=prompt.id))
    
    # GET request - show form
    # Convert tags to comma-separated string for form
    tag_names = ','.join(tag.name for tag in prompt.tags)
    
    return render_template('prompt/edit.html',
                         prompt=prompt,
                         tag_names=tag_names)


@prompt_bp.route('/prompts/<int:id>/delete', methods=['POST'])
@BaseController.handle_service_error
def delete(id):
    """Delete a prompt (soft delete)."""
    success = prompt_service.delete_prompt(id, soft=True)
    
    if success:
        flash('Prompt deleted successfully!', 'success')
    else:
        flash('Prompt not found', 'error')
    
    return redirect(url_for('prompt.index'))


@prompt_bp.route('/prompts/<int:id>/restore', methods=['POST'])
@BaseController.handle_service_error
def restore(id):
    """Restore a deleted prompt."""
    success = prompt_service.restore_prompt(id)
    
    if success:
        flash('Prompt restored successfully!', 'success')
        return redirect(url_for('prompt.view', id=id))
    else:
        flash('Prompt not found', 'error')
        return redirect(url_for('prompt.index'))


@prompt_bp.route('/prompts/<int:id>/archive', methods=['POST'])
@BaseController.handle_service_error
def archive(id):
    """Archive a prompt (set as inactive)."""
    success = prompt_service.archive_prompt(id)
    
    if success:
        flash('Prompt archived successfully!', 'success')
    else:
        flash('Prompt not found', 'error')
    
    return redirect(url_for('prompt.index'))


@prompt_bp.route('/prompts/<int:id>/duplicate', methods=['POST'])
@BaseController.handle_service_error
def duplicate(id):
    """Duplicate a prompt."""
    new_title = request.form.get('title')
    
    try:
        new_prompt = prompt_service.duplicate_prompt(id, new_title)
        flash('Prompt duplicated successfully!', 'success')
        return redirect(url_for('prompt.view', id=new_prompt.id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(request.referrer or url_for('prompt.index'))


@prompt_bp.route('/prompts/merge', methods=['GET', 'POST'])
@BaseController.handle_service_error
def merge():
    """Merge multiple prompts."""
    if request.method == 'POST':
        # Get prompt IDs
        prompt_ids = request.form.getlist('prompt_ids', type=int)
        
        if not prompt_ids:
            flash('No prompts selected for merging', 'error')
            return redirect(url_for('prompt.index'))
        
        # Get merge strategy and options
        strategy = request.form.get('strategy', 'simple')
        options = {
            'include_title': request.form.get('include_title', 'true').lower() == 'true',
            'include_description': request.form.get('include_description', 'false').lower() == 'true'
        }
        
        # Add strategy-specific options
        if strategy == 'separator':
            options['separator'] = request.form.get('separator', '\n\n---\n\n')
        elif strategy == 'template':
            options['template'] = request.form.get('template', '')
        
        # Validate merge
        validation = merge_service.validate_merge(prompt_ids)
        if not validation['valid']:
            for error in validation['errors']:
                flash(error, 'error')
            return redirect(url_for('prompt.index'))
        
        # Show warnings
        for warning in validation['warnings']:
            flash(warning, 'warning')
        
        # Perform merge
        result = merge_service.merge_prompts(prompt_ids, strategy, options)
        
        return render_template('prompt/merge_result.html',
                             merged_content=result['merged_content'],
                             metadata=result['metadata'])
    
    # GET request - show merge form
    # Get selected prompts from query parameters
    prompt_ids = request.args.getlist('ids', type=int)
    
    if not prompt_ids:
        flash('Please select prompts to merge', 'info')
        return redirect(url_for('prompt.index'))
    
    # Get prompts
    from app.repositories import PromptRepository
    prompt_repo = PromptRepository()
    prompts = prompt_repo.get_by_ids(prompt_ids)
    
    if len(prompts) < 2:
        flash('At least 2 prompts required for merging', 'error')
        return redirect(url_for('prompt.index'))
    
    return render_template('prompt/merge.html', prompts=prompts)


@prompt_bp.route('/prompts/search')
def search():
    """Search prompts."""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('prompt.index'))
    
    # Search prompts
    prompts = prompt_service.search_prompts(query)
    
    return render_template('prompt/search.html',
                         prompts=prompts,
                         query=query,
                         count=len(prompts))


@prompt_bp.route('/tags')
def tags():
    """Display tag cloud and statistics."""
    # Get tag cloud
    tag_cloud = tag_service.get_tag_cloud(limit=50)
    
    # Get tag statistics
    statistics = tag_service.get_tag_statistics()
    
    return render_template('tags.html',
                         tag_cloud=tag_cloud,
                         statistics=statistics)


@prompt_bp.route('/tags/cleanup', methods=['POST'])
@BaseController.handle_service_error
def cleanup_tags():
    """Clean up unused tags."""
    deleted_count = tag_service.cleanup_unused_tags()
    
    flash(f'Cleaned up {deleted_count} unused tags', 'success')
    return redirect(url_for('prompt.tags'))