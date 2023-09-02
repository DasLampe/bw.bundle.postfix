global repo
global node

defaults = {
    'postfix': {},
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
