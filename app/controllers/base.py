"""
Base controller with common functionality for all controllers.
Implements shared logic following DRY principle.
"""
from flask import request, jsonify, render_template, redirect, url_for, flash
from functools import wraps
from typing import Dict, Any, Optional, Callable


class BaseController:
    """Base controller class with common methods."""
    
    @staticmethod
    def validate_request_data(required_fields: list) -> Callable:
        """
        Decorator to validate required fields in request data.
        
        Args:
            required_fields: List of required field names
            
        Returns:
            Decorator function
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json() if request.is_json else request.form
                
                missing_fields = []
                for field in required_fields:
                    value = data.get(field)
                    # Handle different types: strings, numbers, etc.
                    if value is None or (isinstance(value, str) and not value.strip()) or value == '':
                        missing_fields.append(field)
                
                if missing_fields:
                    error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                    
                    if request.is_json:
                        return jsonify({'error': error_msg}), 400
                    else:
                        flash(error_msg, 'error')
                        return redirect(request.referrer or '/')
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    @staticmethod
    def handle_service_error(f):
        """
        Decorator to handle service layer errors.
        
        Catches ValueError and other exceptions, returning appropriate responses.
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValueError as e:
                if request.is_json:
                    return jsonify({'error': str(e)}), 400
                else:
                    flash(str(e), 'error')
                    return redirect(request.referrer or '/')
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Service error in {f.__name__}: {str(e)}", exc_info=True)
                
                # In development, show detailed error
                from flask import current_app
                if current_app.config.get('DEBUG', False):
                    error_msg = f"Error: {str(e)}"
                    if request.is_json:
                        return jsonify({'error': error_msg}), 500
                    else:
                        flash(error_msg, 'error')
                        return redirect(request.referrer or '/')
                else:
                    # In production, show generic error
                    if request.is_json:
                        return jsonify({'error': 'An unexpected error occurred'}), 500
                    else:
                        flash('An unexpected error occurred', 'error')
                        return redirect(request.referrer or '/')
        
        return decorated_function
    
    @staticmethod
    def get_request_data() -> Dict[str, Any]:
        """
        Get data from request (JSON or form data).
        
        Returns:
            Dictionary with request data
        """
        if request.is_json:
            return request.get_json() or {}
        else:
            return request.form.to_dict()
    
    @staticmethod
    def get_pagination_params() -> Dict[str, int]:
        """
        Get pagination parameters from request.
        
        Returns:
            Dictionary with 'page' and 'per_page'
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination parameters
        page = max(1, page)
        per_page = max(1, min(100, per_page))  # Max 100 items per page
        
        return {'page': page, 'per_page': per_page}
    
    @staticmethod
    def get_filter_params() -> Dict[str, Any]:
        """
        Get filter parameters from request.
        
        Returns:
            Dictionary with filter parameters
        """
        filters = {}
        
        # Search query
        search = request.args.get('search', '').strip()
        if search:
            filters['search'] = search
        
        # Tag filters
        tags = request.args.getlist('tags')
        if tags:
            filters['tags'] = tags
        
        # Active status filter
        is_active = request.args.get('is_active')
        if is_active is not None:
            if is_active.lower() == 'all':
                # "All" option selected - don't filter by active status
                filters['is_active'] = None
                filters['is_active_explicitly_set'] = True
            elif is_active.lower() == 'true':
                filters['is_active'] = True
                filters['is_active_explicitly_set'] = True
            elif is_active.lower() == 'false':
                filters['is_active'] = False
                filters['is_active_explicitly_set'] = True
            else:
                # Invalid value - default to active
                filters['is_active'] = True
                filters['is_active_explicitly_set'] = False
        else:
            # Default to showing active prompts when no filter is specified
            filters['is_active'] = True
            filters['is_active_explicitly_set'] = False
        
        # Date filters
        created_after = request.args.get('created_after')
        if created_after:
            filters['created_after'] = created_after
        
        created_before = request.args.get('created_before')
        if created_before:
            filters['created_before'] = created_before
        
        # Sorting - these are not model fields, so we'll handle them separately
        sort_by = request.args.get('sort_by', 'order')
        if sort_by in ['created', 'updated', 'title', 'order']:
            filters['sort_by'] = sort_by
        
        sort_order = request.args.get('sort_order', 'asc' if sort_by == 'order' else 'desc')
        if sort_order in ['asc', 'desc']:
            filters['sort_order'] = sort_order
        
        return filters
    
    @staticmethod
    def render_json_or_template(data: Dict[str, Any], 
                               template: Optional[str] = None,
                               status: int = 200):
        """
        Render JSON response or HTML template based on request type.
        
        Args:
            data: Data to render
            template: Template name for HTML response
            status: HTTP status code
            
        Returns:
            JSON response or rendered template
        """
        if request.is_json or 'application/json' in request.headers.get('Accept', ''):
            return jsonify(data), status
        elif template:
            return render_template(template, **data), status
        else:
            # Default to JSON if no template specified
            return jsonify(data), status
    
    @staticmethod
    def success_response(message: str, data: Optional[Dict[str, Any]] = None,
                        redirect_url: Optional[str] = None):
        """
        Create a success response.
        
        Args:
            message: Success message
            data: Additional data
            redirect_url: URL to redirect to (for non-JSON requests)
            
        Returns:
            Appropriate response based on request type
        """
        if request.is_json:
            response = {'success': True, 'message': message}
            if data:
                response.update(data)
            return jsonify(response), 200
        else:
            flash(message, 'success')
            return redirect(redirect_url or request.referrer or '/')
    
    @staticmethod
    def error_response(message: str, status: int = 400,
                      redirect_url: Optional[str] = None):
        """
        Create an error response.
        
        Args:
            message: Error message
            status: HTTP status code
            redirect_url: URL to redirect to (for non-JSON requests)
            
        Returns:
            Appropriate response based on request type
        """
        if request.is_json:
            return jsonify({'error': message}), status
        else:
            flash(message, 'error')
            return redirect(redirect_url or request.referrer or '/')