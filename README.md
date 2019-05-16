# Bundlewrap - Install Postfix

## Dependencies
- mySQL-Bundle (Not published yet)
- [apt-Bundle](https://github.com/sHorst/bw.bundle.apt)

## Config

```
'postfix': {
    'relayhost': '',
    'networks': [],
    'database': {
        'username': 'vmail',
        'password': '[generated]',
        'db': 'vmail',
        'host': '127.0.0.1',
    },
}
```