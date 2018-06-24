pkg_apt = {
    'postfix': {},
    'postfix-mysql': {},
    'mariadb-server': {},
}

svc_systemv = {
    'postfix': {
        'needs': [
            'pkg_apt:postfix',
        ],
    },
    'mysql': {
        'needs': [
            'pkg_apt:mariadb-server',
        ],
    },
}

directories = {
    '/etc/postfix/sasl': {
        'purge': True,
    }
}

files = {
    "/etc/postfix/master.cf": {
        'source': 'etc/postfix/master.cf',
        'content_type': 'mako',
        'mode': '0644',
        'owner': 'root',
        'group': 'root',
    },
    '/etc/postfix/main.cf.proto': {
        'delete': True,
    },
    '/etc/postfix/master.cf.proto': {
        'delete': True,
    },
    "/etc/postfix/virtual": {
        'source': 'etc/postfix/virtual',
        'content_type': 'mako',
        'mode': '0600',
        'owner': 'root',
        'group': 'root',
        'needs': ['pkg_apt:postfix'],
        'triggers': {
            'action:create_virtual_db',
        }
    },
}

if node.metadata.get('postfix', {}).get('relayhost' ''):
    files['/etc/postfix/main.cf'] = {
        'source': 'etc/postfix/main.cf-with-relayhost',
        'content_type': 'mako',
        'mode': '0644',
        'owner': 'root',
        'group': 'root',
        'needs': ['pkg_apt:postfix'],
    }
else:
    files['/etc/postfix/main.cf'] = {
        'source': 'etc/postfix/main.cf',
        'content_type': 'mako',
        'mode': '0644',
        'owner': 'root',
        'group': 'root',
        'needs': ['pkg_apt:postfix'],
    }

actions = {
    'create_virtual_db': {
        'command': 'postmap /etc/postfix/virtual',
        'triggered': True,
        'triggers': {
            #'svc_systemv:postfix:restart'
        },
    },
}
