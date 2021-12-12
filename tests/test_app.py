import pytest
import os
import tempfile
from fahnder.app import create_app

@pytest.fixture
def client():
    app = create_app(config = {
        'CONFIG_FILE': None,
        'ES_DISABLED': True,
        'FAHNDER': {
            'auths': [
                {
                    'module': 'loginpass',
                    'type': 'oauth',
                    'name': 'gitlab',
                    'factory': {
                        'create_gitlab_backend': {
                            'hostname': 'some.gitlab.com'
                        }
                    }
                },
                {
                    'module': 'fahnder.loginpass.jira',
                    'type': 'basic',
                    'name': 'jira',
                    'factory': {
                        'JiraBasic': {
                            'hostname': 'some.jira.com'
                        }
                    },
                }
            ]
        }
    })

    with app.test_client() as client:
        # with app.app_context():
        #    init_db()
        yield client

def test_get_auths(client):
    result = client.get('/api/auths')
    assert result.json == {
        'gitlab': {
            'logged_in': False, 
            'login_url': None, 
            'name': 'gitlab', 
            'type': 'oauth'
            }, 
        'jira': {
            'logged_in': False, 
            'login_url': None, 
            'name': 'jira', 
            'type': 'basic'
        }
    }
