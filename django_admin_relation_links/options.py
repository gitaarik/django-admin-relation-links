from django.urls import reverse
from django.utils.html import format_html


def underscore_to_capitalize(string):
    return string.replace('_', ' ').capitalize()


def get_reverse_relation_name(instance, relation_name):
    for obj in instance._meta.related_objects:
        if obj.name == relation_name:
            return obj.remote_field.name


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

        for field, field_name, options in self.get_change_link_fields():
            if field_name not in fields:
                fields.append(field_name)

        for relation_name, field_name, options in self.get_changelist_link_fields():
            if field_name not in fields:
                fields.append(field_name)

        return fields

    def get_change_link_fields(self):

        for link in self.change_links:

            if type(link) == tuple:
                field, options = (link[0], link[1])
            else:
                field, options = (link, {})
            field_name = '{}_link'.format(field)

            yield field, field_name, options

    def add_change_link_fields(self, readonly_fields):

        for field, field_name, options in self.get_change_link_fields():

            self.add_change_link(field, field_name, options)

            if field_name not in readonly_fields:
                readonly_fields.append(field_name)

    def add_change_link(self, field, field_name, options):

        if self.field_already_set(field_name):
            return

        def make_change_link(field, options):

            def func(instance):
                return self.get_change_link(instance, field, options)
            func.short_description = options.get('label') or '{}'.format(field.replace('_', ' '))

            return func

        setattr(self, field_name, make_change_link(field, options))

    def add_changelist_link_fields(self, readonly_fields):

        for relation_name, field_name, options in self.get_changelist_link_fields():

            self.add_changelist_link(relation_name, field_name, options)

            if field_name not in readonly_fields:
                readonly_fields.append(field_name)

    def get_changelist_link_fields(self):

        for link in self.changelist_links:

            if type(link) == tuple:
                relation_name, options = (link[0], link[1])
            else:
                relation_name, options = (link, {})

            field_name = '{}_link'.format(relation_name)

            yield relation_name, field_name, options

    def add_changelist_link(self, relation_name, field_name, options):

        if self.field_already_set(field_name):
            return

        def make_changelist_link(relation_name, options):

            def func(instance):
                return self.get_changelist_link(instance, relation_name, options)
            func.short_description = options.get('label') or underscore_to_capitalize(relation_name)

            return func

        setattr(self, field_name, make_changelist_link(relation_name, options))

    def field_already_set(self, field_name):
        return getattr(self, field_name, None)

    def get_link_field(self, url, label):
        return format_html('<a href="{}" class="changelink">{}</a>', url, label)

    def get_change_link(self, instance, field, options):
        target_instance = getattr(instance, field)
        return self.get_link_field(
            reverse(
                'admin:{}_{}_change'.format(
                    options.get('app') or target_instance._meta.app_label,
                    options.get('model') or target_instance._meta.model_name
                ),
                args=[target_instance.pk]
            ),
            target_instance
        )

    def get_changelist_link(self, instance, relation_name, options):

        def get_url():
            return reverse(
                'admin:{}_{}_changelist'.format(
                    *self.get_app_model(instance, relation_name, options)
                )
            )

        def get_lookup_filter():
            return options.get('lookup_filter') or get_reverse_relation_name(instance, relation_name)

        def get_label():
            return (
                options.get('label')
                or getattr(instance, relation_name).model._meta.verbose_name_plural.capitalize()
            )

        return self.get_link_field(
            '{}?{}={}'.format(get_url(), get_lookup_filter(), instance.pk),
            get_label()
        )

    def get_app_model(self, instance, relation_name, options):

        options_model = options.get('model')

        if options_model:
            if '.' in options_model:
                app, model = options_model.lower().split('.')
            else:
                app = self.opts.app_label
                model = options_model.lower()
        else:
            model_meta = getattr(instance, relation_name).model._meta
            app = model_meta.app_label
            model = model_meta.model_name

        return app, model
