# Django Admin relation links

An easy way to add links to relations in the Django Admin site.


#### Member list page:
![Member list page](/screenshots/member-list-page.png)
---------------------------

#### Member change page:
![Member change page](/screenshots/member-change-page.png)
---------------------------

#### Group list page:
![Member list page](/screenshots/group-list-page.png)
---------------------------

#### Group change page:
![Member change page](/screenshots/group-change-page.png)


### Install

    pip install django-admin-relation-links


### How to use

The links are placed on the *change page* of the model and go to the *change
list page* or the *change page* of the related model, depending on whether the
related model has a `ForeignKey` to this model or this model has a `ForeignKey`
to the related model, or if it's a `OneToOneField`.

So for example, if you have these models:


```python
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=200)


class Member(models.Model):
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group, related_name='members')
```


Then in the admin you can add links on the `Group` *change page* to the
`Member` *change list page* (all the members of that group) and on the `Member`
*change page* a link to the `Group` *change page* (the group of that member).

```python
from django.contrib import admin
from django_admin_relation_links import AdminChangeLinksMixin


@admin.register(Group)
class GroupAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ['name']
    changelist_links = ['members']  # Use the `related_name` of the `Member.group` field


@admin.register(Member)
class MemberAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ['name']
    change_links = ['group']  # Just specify the name of the `ForeignKey` field
```


### List page links

It is possible to show links on admin *list page* as well, using the field `{field_name}_link`:

```python
@admin.register(Member)
class MemberAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ['name', 'group_link']  # Show link to group *change page* on member *list page*
    change_links = ['group']
```


### Link label

By default, the label of the link is the string representation of the model
instance. You can change the label by creating a method named
`{field_name}_link_label()` like this:

```python
    def group_link_label(self, group):
        return '{} ({} members)'.format(
            group.name,
            group.members.count()
        )
```


### Extra options

You can also set extra options like `label`, `model` and `lookup_filter` like this:

```python
@admin.register(Group)
class GroupAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ['name']
    changelist_links = [
        ('members', {
            'label': 'All members',  # Used as label for the link
            'model': 'Member',  # Specify a different model, you can also specify an app using `app.Member`
            'lookup_filter': 'user_group'  # Specify the GET parameter used for filtering the queryset
        })
    ]
```


### List page ordering

When showing links on the list page, when you use that field for ordering, the
default ordering field is the first field in the `ordering` option on the
`Meta` class of the model of the related field. You can specify an alternative
ordering like this:

```python
@admin.register(Group)
class MemberAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ['name', 'group_link']
    change_links = [
        ('group', {
            'admin_order_field': 'group__name',  # Allow to sort members by `group_link` column
        })
    ]
```
