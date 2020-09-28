import requests


def client():
    if False:
        data = {
            "username": "resttest",
            "email": "test@rest.com",
            "password1": "changeme123",
            "password2": "changeme123"
        }

        response = requests.post("http://127.0.0.1:8000/api/rest-auth/registration/",
                                 data=data)

    token_h = "Token 408fd056def0b8ef5bb27e7603aeca308b27fe8e"
    headers = {"Authorization": token_h}

    response = requests.get("http://127.0.0.1:8000/game_engine/asd/hello",
                            headers=headers)

    print("Status Code: ", response.status_code)

    response_data = response.json()
    print(response_data)


if __name__ == "__main__":
    client()
