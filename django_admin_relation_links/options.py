from django.urls import reverse
from django.utils.html import format_html


def parse_field_config(links_config):

    for link in links_config:

        if isinstance(link, (tuple, list)):
            model_field_name, options = (link[0], link[1])
        else:
            model_field_name, options = (link, {})

        admin_field_name = '{}_link'.format(model_field_name)

        yield model_field_name, admin_field_name, options


def underscore_to_capitalize(string):
    return string.replace('_', ' ').capitalize()


def get_link_field(url, label):
    return format_html('<a href="{}" class="changelink">{}</a>', url, label)


class AdminChangeLinksMixin():

    change_links = []
    changelist_links = []

    def __init__(self, *args, **kwargs):
        super(AdminChangeLinksMixin, self).__init__(*args, **kwargs)
        self._add_change_link_fields()
        self._add_changelist_link_fields()

    def _add_change_link_fields(self):
        for model_field_name, admin_field_name, options in parse_field_config(self.change_links):
            self._add_change_link(model_field_name, admin_field_name, options)

    def _add_change_link(self, model_field_name, admin_field_name, options):

        def make_change_link(model_field_name, options):
            def func(instance):
                return self._get_change_link(instance, model_field_name, admin_field_name, options)
            self.decorate_link_func(func, model_field_name, options)
            return func

        self._add_admin_field(admin_field_name, make_change_link(model_field_name, options))

    def _get_change_link(self, instance, model_field_name, admin_field_name, options):

        target_instance = getattr(instance, model_field_name)

        if not target_instance:
            return

        return get_link_field(
            reverse(
                '{}:{}_{}_change'.format(
                    self.admin_site.name,
                    options.get('app') or target_instance._meta.app_label,
                    options.get('model') or target_instance._meta.model_name
                ),
                args=[target_instance.pk]
            ),
            self.link_label(admin_field_name, target_instance)
        )

    def link_label(self, admin_field_name, target_instance):

        label_method_name = '{}_label'.format(admin_field_name)

        if hasattr(self, label_method_name):
            return getattr(self, label_method_name)(target_instance)

        return str(target_instance)

    def _add_changelist_link_fields(self):
        for model_field_name, admin_field_name, options in parse_field_config(self.changelist_links):
            self._add_changelist_link(model_field_name, admin_field_name, options)

    def _add_changelist_link(self, model_field_name, admin_field_name, options):

        def make_changelist_link(model_field_name, options):
            def func(instance):
                return self._get_changelist_link(instance, model_field_name, options)
            self.decorate_link_func(func, model_field_name, options)
            return func

        self._add_admin_field(admin_field_name, make_changelist_link(model_field_name, options))

    def _get_changelist_link(self, instance, model_field_name, options):

        def get_url():
            return reverse(
                '{}:{}_{}_changelist'.format(
                    self.admin_site.name,
                    *self._get_app_model(instance, model_field_name, options)
                )
            )

        def get_lookup_filter():
            return options.get('lookup_filter') or instance._meta.get_field(model_field_name).field.name

        def get_label():
            return (
                options.get('label')
                or getattr(instance, model_field_name).model._meta.verbose_name_plural.capitalize()
            )

        return get_link_field(
            '{}?{}={}'.format(get_url(), get_lookup_filter(), instance.pk),
            get_label()
        )

    def _get_app_model(self, instance, model_field_name, options):

        options_model = options.get('model')

        if options_model:
            if '.' in options_model:
                app, model = options_model.lower().split('.')
            else:
                app = self.opts.app_label
                model = options_model.lower()
        else:
            model_meta = getattr(instance, model_field_name).model._meta
            app = model_meta.app_label
            model = model_meta.model_name

        return app, model

    def decorate_link_func(self, func, model_field_name, options):

        func.short_description = options.get('label') or underscore_to_capitalize(model_field_name)

        if options.get('admin_order_field'):
            func.admin_order_field = options['admin_order_field']
        else:
            try:
                field = self.model._meta.get_field(model_field_name)
            except:
                pass
            else:
                if (
                    hasattr(field.related_model._meta, 'ordering')
                    and len(field.related_model._meta.ordering) > 0
                ):
                    func.admin_order_field = '{}__{}'.format(
                        field.name,
                        field.related_model._meta.ordering[0].replace('-', '')
                    )

    def _add_admin_field(self, field_name, func):

        if not hasattr(self, field_name):
            setattr(self, field_name, func)

        self._add_field_to_fields(field_name)
        self._add_field_to_readonly_fields(field_name)

    def _add_field_to_fields(self, field_name):
        if self.fields and field_name not in self.fields:
            self.fields = list(self.fields) + [field_name]

    def _add_field_to_readonly_fields(self, field_name):

        if not self.readonly_fields:
            self.readonly_fields = []

        if field_name not in self.readonly_fields:
            self.readonly_fields = list(self.readonly_fields) + [field_name]
