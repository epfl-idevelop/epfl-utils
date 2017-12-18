"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import ldap3

from epflldap.utils import get_optional_env, EpflLdapException


def _get_LDAP_connection():
    """
    Return a LDAP connection
    """
    server = ldap3.Server('ldap://' + get_optional_env('EPFL_LDAP_SERVER_FOR_SEARCH'))
    connection = ldap3.Connection(server)
    connection.open()

    return connection, get_optional_env('EPFL_LDAP_BASE_DN')


def LDAP_search(pattern_search, attribute):
    """
    Do a LDAP search
    """
    connection, ldap_base = _get_LDAP_connection()

    connection.search(
        search_base=ldap_base,
        search_filter=pattern_search,
        attributes=[attribute]
    )
    return connection.response


def is_unit_exist(unit_id):
    """
    Return True if the unit 'unid_id' exists.
    Otherwise return False
    """
    try:
        attribute = 'objectClass'
        response = LDAP_search(
            pattern_search="(uniqueidentifier={})".format(unit_id),
            attribute=attribute
        )
        return 'EPFLorganizationalUnit' in response[0]['attributes'][attribute]
    except Exception:
        return False


def get_unit_name(unit_id):
    """
    Return the unit name to the unit 'unit_id'
    """
    try:
        attribute = 'cn'
        response = LDAP_search(
            pattern_search='(uniqueIdentifier={})'.format(unit_id),
            attribute=attribute
        )
        unit_name = response[0]['attributes'][attribute][0]
    except Exception:
        raise EpflLdapException("The unit with id '{}' was not found".format(unit_id))

    return unit_name


def get_unit_id(unit_name):
    """
    Return the unit id to the unit 'unit_name'
    """
    attribute = 'uniqueIdentifier'
    response = LDAP_search(
        pattern_search='(cn={})'.format(unit_name),
        attribute=attribute
    )

    unit_id = ""
    for element in response:
        if 'dn' in element and element['dn'].startswith('ou={},'.format(unit_name)):
            unit_id = element['attributes'][attribute][0]

    if not unit_id:
        raise EpflLdapException("The unit named '{}' was not found".format(unit_name))

    return unit_id


def get_units(username):
    """
    Return all units of user 'username'
    """
    connection, ldap_base = _get_LDAP_connection()

    # Search the user dn
    connection.search(
        search_base=ldap_base,
        search_filter='(uid={}@*)'.format(username),
    )

    # For each user dn give me the unit
    dn_list = [connection.response[index]['dn'] for index in range(len(connection.response))]

    units = []
    # For each unit search unit information and give me the unit id
    for dn in dn_list:
        unit = dn.split(",ou=")[1]
        connection.search(search_base=ldap_base, search_filter='(ou={})'.format(unit), attributes=['uniqueidentifier'])
        units.append(connection.response[0]['attributes']['uniqueIdentifier'][0])

    return units


def get_sciper(username):
    """
    Return the sciper of user
    """
    try:
        attribute = 'uniqueIdentifier'
        response = LDAP_search(
            pattern_search='(uid={})'.format(username),
            attribute=attribute
        )
        return response[0]['attributes'][attribute][0]
    except Exception:
        raise EpflLdapException("No sciper corresponds to username {}".format(username))

    return username


def get_username(sciper):
    """
    Return username of user
    """
    try:
        attribute = 'uid'
        response = LDAP_search(
            pattern_search='(uniqueIdentifier={})'.format(sciper),
            attribute=attribute
        )
        username = response[0]['attributes'][attribute][0]
    except Exception:
        raise EpflLdapException("No username corresponds to sciper {}".format(sciper))

    return username


def get_email(sciper):
    """
    Return email of user
    """
    try:
        attribute = 'mail'
        response = LDAP_search(
            pattern_search='(uniqueIdentifier={})'.format(sciper),
            attribute=attribute
        )
        email = response[0]['attributes'][attribute][0]
    except Exception:
        raise EpflLdapException("No email address corresponds to sciper {}".format(sciper))

    return email
