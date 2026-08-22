import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-me')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://ctfuser:ctfpassword@ctf-db/ctfapp'
    )

    # LDAP settings
    LDAP_HOST = '192.168.151.10'
    LDAP_PORT = 389
    LDAP_USE_SSL = False
    LDAP_BASE_DN = 'dc=ctf,dc=local'
    LDAP_USER_DN = 'CTF-Users'
    LDAP_GROUP_DN = 'Groups'
    LDAP_USER_RDN_ATTR = 'cn'
    LDAP_USER_LOGIN_ATTR = 'sAMAccountName'
    LDAP_USER_SEARCH_SCOPE = 'SUBTREE'
    LDAP_GROUP_SEARCH_SCOPE = 'SUBTREE'
    LDAP_BIND_USER_DN = None
    LDAP_BIND_USER_PASSWORD = None
    LDAP_ALWAYS_SEARCH_BIND = True
