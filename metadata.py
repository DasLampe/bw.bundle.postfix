global repo
global node

defaults = {
    'postfix': {
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
