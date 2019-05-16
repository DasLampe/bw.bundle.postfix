@metadata_processor
def add_apt_packages(metadata):
    if node.has_bundle("apt"):
        metadata.setdefault('apt', {})
        metadata['apt'].setdefault('packages', {})

        metadata['apt']['packages']['postfix'] = {'installed': True}
        metadata['apt']['packages']['postfix-mysql'] = {'installed': True}
        metadata['apt']['packages']['mysql-server'] = {'installed': True}

    return metadata, DONE
