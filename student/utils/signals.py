from simple_history.models import HistoricalRecords


def add_history_ip_address(sender, **kwargs):
    history_instance = kwargs['history_instance']
    print("geldi")
    # thread.request for use only when the simple_history middleware is on and enabled
    #history_instance.ip_address = HistoricalRecords.thread.request.META['REMOTE_ADDR']
