class ActivePageMixin(object):
    active_page = ''

    def get_context_data(self, **kwargs):
        context = super(ActivePageMixin, self).get_context_data(**kwargs)
        context['active_page'] = self.active_page
        return context
