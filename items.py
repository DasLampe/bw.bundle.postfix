# noinspection PyGlobalUndefined
global node
# noinspection PyGlobalUndefined
global repo

mysql_user = node.metadata.get('postfix', {}).get('database', {}).get('user', 'vmail')
mysql_password = node.metadata.get('postfix', {}).get('database', {}).\
    get('password', repo.libs.pw.get("mysql_{}_user_{}".format(mysql_user, node.name)))
mysql_host = node.metadata.get('postfix', {}).get('database', {}).get('host', '127.0.0.1')
mysql_db = node.metadata.get('postfix', {}).get('database', {}).get('db', 'vmail')


pkg_apt = {
    'postfix': {},
    'postfix-mysql': {},
}

svc_systemv = {
    'postfix': {
        'needs': [
            'pkg_apt:postfix',
        ],
    },
    'mysql': {
        'needs': [
            'pkg_apt:mysql-server',
        ],
    },
}

directories = {
    '/etc/postfix/sasl': {
        'purge': True,
    },
    '/etc/postfix/virtual': {
        'mode': '0640',
        'owner': 'root',
        'group': 'root',
    },
}

files = {
    #Cleanup
    '/etc/postfix/main.cf.proto': {
        'delete': True,
    },
    '/etc/postfix/master.cf.proto': {
        'delete': True,
    },

    "/etc/postfix/master.cf": {
        'source': 'etc/postfix/master.cf',
        'content_type': 'mako',
        'mode': '0644',
        'owner': 'root',
        'group': 'root',
    },

    #Get accounts, redirect and some stuff from database
    '/etc/postfix/virtual/accounts.cf': {
        'source': 'etc/postfix/virtual/accounts.cf',
        'content_type': 'mako',
        'mode': '0640',
        'owner': 'root',
        'group': 'root',
        'context': {
            'mysql_user': mysql_user,
            'mysql_password': mysql_password,
            'mysql_db': mysql_db,
            'mysql_host': mysql_host,
        }
    },
    '/etc/postfix/virtual/aliases.cf': {
        'source': 'etc/postfix/virtual/aliases.cf',
        'content_type': 'mako',
        'mode': '0640',
        'owner': 'root',
        'group': 'root',
        'context': {
            'mysql_user': mysql_user,
            'mysql_password': mysql_password,
            'mysql_db': mysql_db,
            'mysql_host': mysql_host,
        }
    },
    '/etc/postfix/virtual/domains.cf': {
        'source': 'etc/postfix/virtual/domains.cf',
        'content_type': 'mako',
        'mode': '0640',
        'owner': 'root',
        'group': 'root',
        'context': {
            'mysql_user': mysql_user,
            'mysql_password': mysql_password,
            'mysql_db': mysql_db,
            'mysql_host': mysql_host,
        }
    },
    '/etc/postfix/virtual/recipient-access.cf': {
        'source': 'etc/postfix/virtual/recipient-access.cf',
        'content_type': 'mako',
        'mode': '0640',
        'owner': 'root',
        'group': 'root',
        'context': {
            'mysql_user': mysql_user,
            'mysql_password': mysql_password,
            'mysql_db': mysql_db,
            'mysql_host': mysql_host,
        }
    },
    '/etc/postfix/virtual/sender-login-maps.cf': {
        'source': 'etc/postfix/virtual/sender-login-maps.cf',
        'content_type': 'mako',
        'mode': '0640',
        'owner': 'root',
        'group': 'root',
        'context': {
            'mysql_user': mysql_user,
            'mysql_password': mysql_password,
            'mysql_db': mysql_db,
            'mysql_host': mysql_host,
        }
    },
    '/etc/postfix/virtual/tls-policy.cf': {
        'source': 'etc/postfix/virtual/tls-policy.cf',
        'content_type': 'mako',
        'mode': '0640',
        'owner': 'root',
        'group': 'root',
        'context': {
            'mysql_user': mysql_user,
            'mysql_password': mysql_password,
            'mysql_db': mysql_db,
            'mysql_host': mysql_host,
        }
    },

    # Place SQL-Structure file
    '/etc/postfix/sql/structure.sql': {
        'source': 'etc/postfix/sql/structure.sql',
        'content_type': 'mako',
        'mode': '640',
        'owner': 'root',
        'group': 'root',
        'triggers': {
            'action:deploy_postfix_mysql_structure',
        }
    }
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

actions = {
    'deploy_postfix_mysql_structure': {
        'command': 'cat /etc/postfix/sql/structure.sql | mysql --defaults-file=/etc/mysql/debian.cnf',
        'expected_return_code': 0,
        'triggered': True,
        'needs': [
            'bundle:mysql',
            'pkg_apt:mysql-server',
        ],
    },
}
