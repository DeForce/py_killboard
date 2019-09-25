from killboard.schema.killmail import Killmail


def write_killmail(km_dict, client):
    km_id = km_dict['killmail_id']
    create = False
    if Killmail.objects.filter(id=km_id).exists():
        km = Killmail.objects.get(id=km_id)
        km.update_mail(km_dict, client)
    else:
        create = True
        km = Killmail()
        km.create_mail(km_dict, client)
    km.save()
    return create


def get_killmail_data(k_hash, k_id, client):
    data = client.Killmails.get_killmails_killmail_id_killmail_hash(
        killmail_hash=k_hash, killmail_id=k_id)
    return data.result()


def download_killmails(killmails, client):
    for km in killmails:
        yield write_killmail(get_killmail_data(km['killmail_hash'], km['killmail_id'], client), client)

