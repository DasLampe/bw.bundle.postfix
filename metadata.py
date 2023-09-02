global repo
global node

defaults = {
    'postfix': {
        'mynetworks': [],
        'myhostname': node.hostname,
        'mydestination': node.hostname,
        'max_queue_lifetime': '1h',
        'bounce_queue_lifetime': '1h',
        'max_backoff_time': '15m',
        'min_backoff_time': '5m',
        'queue_run_delay': '5m',
        'max_msg_size': 52428800,

        'ssl_cert': f'/etc/letsencrypt/{node.hostname}/live/fullchain.pem',
        'ssl_key': f'/etc/letsencrypt/{node.hostname}/live/privkey.pem',

        'rspamd_enabled': node.has_bundle('rspamd'),

        'database': {
            'user': 'vmail_bw',
            'password': repo.vault.password_for("mysql_{}_user_{}".format('vmail_bw', node.name)),
            'host': 'localhost',
            'db': 'vmail_bw',
        }
    },
}

@metadata_reactor
def add_iptables(metadata):
    meta_tables = {}
    if node.has_bundle("iptables"):
        meta_tables += repo.libs.iptables.accept().chain('INPUT').dest_port('465').protocol('tcp')
        meta_tables += repo.libs.iptables.accept().chain('INPUT').dest_port('587').protocol('tcp')
        meta_tables += repo.libs.iptables.accept().chain('INPUT').dest_port('25').protocol('tcp')

        # Outgoing mails
        meta_tables += repo.libs.iptables.accept().chain('OUTPUT').dest_port('25').protocol('tcp')
        meta_tables += repo.libs.iptables.accept().chain('OUTPUT').dest_port('465').protocol('tcp')
    return meta_tables
