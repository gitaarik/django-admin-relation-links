# Django Admin relation links

An easy way to add links to relations in the Django Admin site.

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
    group = models.ForeignKey(Group)
```


Then in the admin you can add links on the `Group` *change page* to the
`Member` *change list page* (all the members of that group) and on the `Member`
*change page* a link to the `Group` *change page* (the group of that member).

```python
from django.contrib import admin
from admin_relation_links import AdminChangeLinksMixin


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin, AdminChangeLinksMixin):
    list_display = ['name']
    changelist_links = ['member']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin, AdminChangeLinksMixin):
    list_display = ['name']
    change_links = ['group']
```


### Extra options

You can also set extra options like `label` and `lookup_filter` like this:

```python
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin, AdminChangeLinksMixin):
    list_display = ['name']
    changelist_links = [
        ('member', {
            'label': 'All members',
            'lookup_filter': 'user_group'
        })
    ]
```

So instead of the string of the related model, you use a tuple where the first
item is the name of the related model, and the second item is a dict with the
extra options. The `label` parameter sets the label used for the link in the
admin interface. The `lookup_filter` parameter sets the GET param used for
filtering in the URL. By default that's the lowercase name of the model, but
that might not always be the same on the related object.
