global repo
global node

@metadata_processor
def add_iptables(metadata):
    if node.has_bundle("iptables"):
        metadata += repo.libs.iptables.accept().chain('INPUT').dest_port('465').protocol('tcp')
        metadata += repo.libs.iptables.accept().chain('INPUT').dest_port('587').protocol('tcp')
        metadata += repo.libs.iptables.accept().chain('INPUT').dest_port('25').protocol('tcp')
        # Outgoing mails
        metadata += repo.libs.iptables.accept().chain('OUTPUT').dest_port('25').protocol('tcp')
        metadata += repo.libs.iptables.accept().chain('OUTPUT').dest_port('465').protocol('tcp')
    return metadata, DONE
