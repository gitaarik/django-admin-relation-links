# Django Admin relation links

An easy way to add links to relations in the Django Admin site.

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
`Member` *change list page* (a link to all the members of that group) and on
the `Member` *change page* a link to the `Group` *change page* (a link to the
group of that member).

```python
from django.contrib import admin
from admin_relation_links import AdminChangeLinksMixin


@admin.register(Group)
class GroupAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ['name']
    changelist_links = ['member']


@admin.register(Member)
class MemberAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ['name']
    change_links = ['group']
```
