"""Admin controller: Users management and allowlist CRUD (MVP)."""
from typing import Optional
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from app.repositories.user_repository import UserRepository
from app.repositories.allowlist_repository import AllowlistRepository


admin_bp = Blueprint('admin', __name__)
user_repo = UserRepository()
allowlist_repo = AllowlistRepository()


def admin_required():
    if not current_user.is_authenticated or getattr(current_user, 'role', '') != 'admin':
        from flask import abort
        abort(403)


@admin_bp.route('/admin/users')
@login_required
def users_index():
    admin_required()
    status = request.args.get('status', 'pending')
    if status not in ('pending', 'active', 'disabled'):
        status = 'pending'
    users = user_repo.list_by_status(status)
    return render_template('admin/users.html', users=users, current_status=status)


@admin_bp.route('/admin/users/<int:user_id>/approve', methods=['POST'])
@login_required
def users_approve(user_id: int):
    admin_required()
    role = request.form.get('role') or None
    from app.services.user_service import UserService
    service = UserService()
    current_app.logger.info('Admin action: approve_user start. target_user_id=%s, by_admin_id=%s, role=%s', user_id, getattr(current_user, 'id', None), role)
    service.approve_user(user_id, approver_user_id=current_user.id, role=role)
    current_app.logger.info('Admin action: approve_user done. target_user_id=%s, by_admin_id=%s', user_id, getattr(current_user, 'id', None))
    flash('User approved', 'success')
    return redirect(url_for('admin.users_index', status='pending'))


@admin_bp.route('/admin/users/<int:user_id>/disable', methods=['POST'])
@login_required
def users_disable(user_id: int):
    admin_required()
    from app.services.user_service import UserService
    service = UserService()
    current_app.logger.info('Admin action: disable_user start. target_user_id=%s, by_admin_id=%s', user_id, getattr(current_user, 'id', None))
    service.disable_user(user_id)
    current_app.logger.info('Admin action: disable_user done. target_user_id=%s, by_admin_id=%s', user_id, getattr(current_user, 'id', None))
    flash('User disabled', 'info')
    return redirect(url_for('admin.users_index', status='active'))


@admin_bp.route('/admin/allowlist', methods=['GET', 'POST'])
@login_required
def allowlist_index():
    admin_required()
    if request.method == 'POST':
        email = request.form.get('email')
        default_role = request.form.get('default_role') or 'user'
        note = request.form.get('note') or None
        try:
            current_app.logger.info('Admin action: allowlist_add start. by_admin_id=%s', getattr(current_user, 'id', None))
            allowlist_repo.add(email=email, default_role=default_role, note=note)
            current_app.logger.info('Admin action: allowlist_add done. by_admin_id=%s', getattr(current_user, 'id', None))
            flash('Allowlist entry added', 'success')
        except Exception as exc:
            current_app.logger.warning('Failed to add allowlist entry: %s', exc)
            flash('Failed to add allowlist entry', 'error')
        return redirect(url_for('admin.allowlist_index'))

    entries = allowlist_repo.list_all()
    return render_template('admin/allowlist.html', entries=entries)


@admin_bp.route('/admin/allowlist/<int:entry_id>/remove', methods=['POST'])
@login_required
def allowlist_remove(entry_id: int):
    admin_required()
    current_app.logger.info('Admin action: allowlist_remove start. entry_id=%s, by_admin_id=%s', entry_id, getattr(current_user, 'id', None))
    ok = allowlist_repo.remove_by_id(entry_id)
    current_app.logger.info('Admin action: allowlist_remove done. entry_id=%s, by_admin_id=%s, success=%s', entry_id, getattr(current_user, 'id', None), ok)
    flash('Allowlist entry removed' if ok else 'Allowlist entry not found', 'info')
    return redirect(url_for('admin.allowlist_index'))


