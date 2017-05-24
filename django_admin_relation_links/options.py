import re
from django.core.urlresolvers import reverse
from django.utils.html import format_html


def camel_case_to_underscore(string):
    return re.sub(r'(?!^)([A-Z]+)', r'_\1', string).lower()


class AdminChangeLinksMixin():

    change_links = []
    changelist_links = []

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj=None))
        self.add_change_link_fields(readonly_fields)
        self.add_changelist_link_fields(readonly_fields)
        return readonly_fields

    def get_fields(self, request, obj=None):

        fields = list(super().get_fields(request, obj=None))

        if not fields:
            return fields

        for link_name, field_name, options in self.get_change_link_fields():
            if field_name not in fields:
                fields.append(field_name)

        for link_name, field_name, options in self.get_changelist_link_fields():
            if field_name not in fields:
                fields.append(field_name)

        return fields

    def get_change_link_fields(self):

        for link in self.change_links:

            if type(link) == tuple:
                link_name, options = (link[0], link[1])
            else:
                link_name, options = (link, {})
            field_name = '{}_change_link'.format(link_name)

            yield link_name, field_name, options

    def add_change_link_fields(self, readonly_fields):

        for link_name, field_name, options in self.get_change_link_fields():

            self.add_change_link(link_name, field_name, options)

            if field_name not in readonly_fields:
                readonly_fields.append(field_name)

    def add_change_link(self, field, field_name, options):

        if self.field_already_set(field_name):
            return

        def make_change_link(field, options):

            def func(instance):
                return self.get_change_link(instance, field, **options)

            func.short_description = (
                options.get('label')
                or '{}'.format(field.replace('_', ' '))
            )

            return func

        setattr(self, field_name, make_change_link(field, options))

    def add_changelist_link_fields(self, readonly_fields):

        for link_name, field_name, options in self.get_changelist_link_fields():

            self.add_changelist_link(link_name, field_name, options)

            if field_name not in readonly_fields:
                readonly_fields.append(field_name)

    def get_changelist_link_fields(self):

        for link in self.changelist_links:

            if type(link) == tuple:
                link_name, options = (link[0], link[1])
            else:
                link_name, options = (link, {})

            field_name = '{}_changelist_link'.format(link_name)

            yield link_name, field_name, options

    def add_changelist_link(self, field, field_name, options):

        if self.field_already_set(field_name):
            return

        def make_changelist_link(field, options):

            def func(instance):
                return self.get_changelist_link(instance, field, **options)

            func.short_description = (
                options.get('label')
                or '{}s'.format(field)
            )

            return func

        setattr(self, field_name, make_changelist_link(field, options))

    def field_already_set(self, field_name):
        return getattr(self, field_name, None)

    def get_link_field(self, url, label):
        return format_html('<a href="{}" class="changelink">{}</a>', url, label)

    def get_change_link(self, instance, field):
        target_instance = getattr(instance, field)
        return self.get_link_field(
            reverse(
                'admin:{}_{}_change'.format(
                    self.opts.app_label,
                    target_instance._meta.model_name
                ),
                args=[target_instance.id]
            ),
            target_instance
        )

    def get_changelist_link(self, instance, target_model_name, lookup_filter=None, label=None):

        def get_url():
            return reverse(
                'admin:{}_{}_changelist'.format(
                    self.opts.app_label,
                    target_model_name.replace('_', '')
                )
            )

        def get_lookup_filter():
            return lookup_filter or camel_case_to_underscore(instance._meta.object_name)

        def get_label():
            return label or '{}s'.format(target_model_name.replace('_', ' ').capitalize())

        return self.get_link_field(
            '{}?{}={}'.format(get_url(), get_lookup_filter(), instance.id),
            get_label()
        )
