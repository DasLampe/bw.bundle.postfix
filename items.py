# noinspection PyGlobalUndefined
global node
# noinspection PyGlobalUndefined
global repo

mysql_user = node.metadata.get('postfix', {}).get('database', {}).get('user', 'vmail_bw')
mysql_password = node.metadata.get('postfix', {}).get('database', {}). \
    get('password', repo.vault.password_for("mysql_{}_user_{}".format(mysql_user, node.name)))
mysql_host = node.metadata.get('postfix', {}).get('database', {}).get('host', '127.0.0.1')
mysql_db = node.metadata.get('postfix', {}).get('database', {}).get('db', 'vmail_bw')

pkg = {
    'postfix': {
        'installed': True,
    },
    'postfix-mysql': {
        'installed': True,
    },
}
actions = {}
files = {}
directories = {}

####
# Create MySQL Structure
####

# Create Database and user
if mysql_host == 'localhost' or mysql_host == '127.0.0.1':
    mysql_users = {
        mysql_user: {
            'password': mysql_password,
            'hosts': ['127.0.0.1', '::1', 'localhost'].copy(),
            'db_priv': {
                mysql_db: 'all',
            },
        },
    }

    mysql_dbs = {
        mysql_db: {
            'triggers': {
                'action:deploy_postfix_mysql_structure',
            },
        },
    }

files['/tmp/structure.sql'] = {
    'source': 'structure.sql',
}

actions['deploy_postfix_mysql_structure'] = {
    'command':  'mysql -u {mysql_user} -p{mysql_password} {mysql_db} < /tmp/structure.sql && rm /tmp/structure.sql'
                .format(mysql_user=mysql_user, mysql_password=mysql_password, mysql_db=mysql_db),
    'needs': [
        'file:/tmp/structure.sql',
    ],
    'triggered': True,
}

for file in ['tls-policy.cf', 'sender-login-maps.cf', 'recipient-access.cf', 'domains.cf', 'aliases.cf', 'accounts.cf']:
    files['/etc/postfix/sql/{}'.format(file)] = {
        'source': 'etc/postfix/sql/{}'.format(file),
        'content_type': 'mako',
        'context': {
            'mysql_user': mysql_user,
            'mysql_password': mysql_password,
            'mysql_db': mysql_db,
            'mysql_host': mysql_host,
        },
        'owner': 'postfix',
        'group': 'postfix',
        'mode': '640',
    }

####
# Create vmail-User
####
actions['add_vmail_user'] = {
    'command': 'adduser --disabled-login --disabled-password --home /var/vmail vmail',
    'unless': 'getent passwd vmail  > /dev/null',
}

directories['/var/vmail'] = {
    'owner': 'vmail',
    'group': 'vmail',
    'mode': '0770',
    'needs': [
        'action:add_vmail_user',
    ],
}

directories['/var/vmail/mailboxes'] = {
    'owner': 'vmail',
    'group': 'vmail',
    'mode': '0770',
}

# Clean up
directories['/etc/postfix/sasl'] = {
    'purge': True,
}

for file in ['master.cf', 'main.cf.proto', 'master.cf.proto']:
    files['/etc/postfix/{}'.format(file)] = {
        'delete': True,
    }

# Generate Files
config = node.metadata.get('postfix', {})

files['/etc/postfix/main.cf'] = {
    'source': 'etc/postfix/main.cf',
    'content_type': 'mako',
    'context': {
        'mynetworks': config.get('mynetworks', []),
        'myhostname': node.hostname,
        'mydestination': config.get('mydestination', node.hostname),
        'max_queue_lifetime': config.get('max_queue_lifetime', '1h'),
        'bounce_queue_lifetime': config.get('bounce_queue_lifetime', '1h'),
        'max_backoff_time': config.get('max_backoff_time', '15m'),
        'min_backoff_time': config.get('min_backoff_time', '5m'),
        'queue_run_delay': config.get('queue_run_delay', '5m'),
        'smtpd_tls_cert_file': config.get('ssl_cert', '/etc/letsencrypt/{}/live/fullchain.pem'.format(node.hostname)),
        'smtpd_tls_key_file': config.get('ssl_key', '/etc/letsencrypt/{}/live/privkey.pem'.format(node.hostname)),
        'rspamd': node.has_bundle('rspamd'),
        'max_msg_size': config.get('max_msg_size', 52428800),
    }
}

files['/etc/postfix/master.cf'] = {
    'source': 'etc/postfix/master.cf',
}

files['/etc/postfix/submission_header_cleanup'] = {
    'source': 'etc/postfix/submission_header_cleanup',
}

files['/etc/postfix/without_ptr'] = {
    'source': 'etc/postfix/without_ptr',
    'triggers': {
        'action:postmap_without_ptr',
    },
}

files['/etc/postfix/postscreen_access'] = {
    'source': 'etc/postfix/postscreen_access',
    'owner': 'postfix',
    'group': 'postfix',
}

actions['postmap_without_ptr'] = {
    'command': 'postmap /etc/postfix/without_ptr',
    'triggered': True,
    'needs': [
        'pkg:postfix',
    ],
}

actions['generate_aliases.db'] = {
    'command': 'newaliases',
    'needs': [
        'pkg:postfix',
    ],
}
