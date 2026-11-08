from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from apps.auths.forms import CustomUserChangeForm, CustomUserCreationForm
from apps.auths.models import User

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm

    ordering = ('email',)
    list_display = ('user_header', 'active_label', 'staff_label', 'posts_count')
    list_filter_submit = True
    list_filter = (('is_active', BooleanRadioFilter), ('is_staff', BooleanRadioFilter))
    search_fields = ('email', 'first_name', 'last_name')
    actions = ['activate_users', 'deactivate_users']

    fieldsets = (
        ('Personal info', {'classes': ['tab'], 'fields': ('email', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'classes': ['tab'], 'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'classes': ['tab'], 'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        return super().get_queryset(request).annotate(p_cnt=Count('posts'))

    @display(description='User', header=True)
    def user_header(self, obj: User) -> list[str]:
        name = f'{obj.first_name} {obj.last_name}'.strip() or obj.email
        initials = f'{obj.first_name[:1]}{obj.last_name[:1]}'.upper() or 'U'
        return [name, obj.email, initials]

    @display(description='Active', label={'Active': 'success', 'Inactive': 'danger'})
    def active_label(self, obj: User) -> str:
        return 'Active' if obj.is_active else 'Inactive'

    @display(description='Staff', label={'Staff': 'info', 'No': 'secondary'})
    def staff_label(self, obj: User) -> str:
        return 'Staff' if obj.is_staff else 'No'

    @display(description='Posts', ordering='p_cnt')
    def posts_count(self, obj: User) -> int:
        return getattr(obj, 'p_cnt', 0)

    @action(description='Activate selected users')
    def activate_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        queryset.update(is_active=True)

    @action(description='Deactivate selected users')
    def deactivate_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        queryset.update(is_active=False)