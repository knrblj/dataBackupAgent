import requests

def generate_access_token(zoho_config):
    """
    Generate an access token for Zoho API using the provided configuration.

    :param zoho_config: Dictionary containing Zoho configuration.
    :return: Access token as a string.
    """
    url = "https://accounts.zoho.com/oauth/v2/token"
    payload = {
        'grant_type': 'refresh_token',
        'client_id': zoho_config['client_id'],
        'client_secret': zoho_config['client_secret'],
        'refresh_token': zoho_config['refresh_token']
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Failed to generate access token: {response.text}")