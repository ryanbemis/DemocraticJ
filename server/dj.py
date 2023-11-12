import requests
import webbrowser
import http.server
import urllib.parse
import base64
import json
import pprint
import dj_requests as djr
from urllib.parse import urlencode

auth_values = None
current_state = 0
cur_track = 0
access_token = None
tracks = [
    {
       "name": "Sh-Boom",
       "id": "2drXvACELcvwryaFRiRPdA",
       "art": "https://i.scdn.co/image/ab67616d0000b27315b2cfd135d4eaba438066ce",
       "artist": "The Chords"
    },
    {
        'art': 'https://i.scdn.co/image/ab67616d0000b273bbf0146981704a073405b6c2', 
        'artist': 'Aerosmith', 
        'id': '1xsYj84j7hUDDnTTerGWlH', 
        'name': 'Dream On'
    },
    {
        "name": "Busy Earnin'",
        "art": "https://i.scdn.co/image/ab67616d0000b27344fee73b385fdcc0e07922f9",
        "id": "5TloYFwzd09yWy8xkRLVUu",
        "artist": "Jungle"
    },
    {
        "name": "No Church in the Wild",
        "art": "https://i.scdn.co/image/ab67616d0000b27352e61456aa4995ba48d94e30",
        "artist": "JAY-Z, Kanye West",
        "id": "7r6PigmGzlB3YPB7wvBBbi"
    },
    {
        'art': 'https://i.scdn.co/image/ab67616d0000b273ea7caaff71dea1051d49b2fe', 
        'artist': 'Pink Floyd', 
        'id': '0vFOzaXqZHahrZp6enQwQb', 
        'name': 'Money'
    },
    {
        "name": "It Wasn't Me",
        "art": "https://i.scdn.co/image/ab67616d0000b2739449f9491c364d28a9668e17",
        "id": "3WkibOpDF7cQ5xntM1epyf",
        "artist": "Shaggy, Rik Rok"
    },
    {
        'art': 'https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36', 
        'artist': 'The Weeknd', 
        'id': '0VjIjW4GlUZAMYd2vXMi3b', 
        'name': 'Blinding Lights'
    }
]

class TestHTTPHandler (http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global current_state
        if (current_state == 0):
            global auth_values
            self.send_response(200)
            self.end_headers()
            auth_values = urllib.parse.parse_qs(self.path)
            self.wfile.write(bytes("Logged in!", "utf-8"))
            current_state += 1
        else:
            global cur_track
            print("PATH: " + self.path)

            # Ignore icon requests
            if (self.path == "/favicon.ico"):
                self.send_response(200)
                self.end_headers()
            elif (self.path == "/cur_poll" and cur_track < len(tracks)):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(json.dumps(tracks[cur_track]), "utf-8"))
                return
            elif (self.path == "/vote_yes"): # Check if it should be added to the queue
                addTrackToQueue(cur_track)

            # If the person voted no, don't add it and instead just move on

            cur_track += 1
            if cur_track >= len(tracks):
                cur_track = 0

            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes("Still more", "utf-8"))

def addTrackToQueue(index):
    global access_token
    # Add to queue
    print("Added index: " + str(index))
    player_headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
    }

    player_data = {
        "uris": [f'spotify:track:{tracks[index]["id"]}'],
        "position_ms": 0
    }

    print("\n\n")
    print(json.dumps(player_data))

    player_response = requests.put("https://api.spotify.com/v1/me/player/play", headers=player_headers, data=json.dumps(player_data))
    print(f'({player_response.status_code},{player_response.reason})')

def populate_tracks():
    global tracks

if __name__ == '__main__':
    client_id = "c212ec5691774302a63a3995dd605e16"
    client_secret = "b186c5b6f4b0428083b367f449576c72"
    host_name = "localhost"
    redirect_uri = f"http://{host_name}:8080"

    query_params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "user-modify-playback-state user-read-playback-state",
        "show_dialog": "true"
    }

    query_str = urlencode(query_params)

    # urllib.request.urlopen(url, data=None, [timeout, ]*, cafile=None, capath=None, cadefault=False, context=None)
    auth_response = requests.get("https://accounts.spotify.com/authorize?"+query_str)

    print(auth_response.url)

    if auth_response.status_code == 200:
        webbrowser.open(auth_response.url)
        test_server = http.server.HTTPServer((host_name, 8080), TestHTTPHandler)
        test_server.handle_request()

        # Now we have a valid auth token, need to get access token
        access_token_dict = {
            "grant_type": "authorization_code",
            "code": auth_values["/?code"],
            "redirect_uri": redirect_uri
        }

        base64Str = bytes(client_id+":"+client_secret, "utf-8")
        base64Enc = base64.b64encode(base64Str)
        print(f'\n{base64Enc.decode()}\n')

        access_headers = {
            "Authorization": "Basic " + base64Enc.decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        print(access_headers)

        access_response = requests.post(url="https://accounts.spotify.com/api/token", data=access_token_dict, headers=access_headers)
        access_response_dict = json.loads(access_response.content.decode())
        print(f'\n{access_response_dict}')

        # Now have access_token
        if ("access_token" not in access_response_dict):
            print("\nError Getting Access Token: \n" + access_response.content.decode())
            exit(-1)

        access_token = access_response_dict['access_token']

        search_query = {
            "q": "it wasn't me",
            "type": "track",
            "limit": "1"
        }

        search_headers = {
            "Authorization": "Bearer " + access_token
        }

        # response = requests.get("https://api.spotify.com/v1/search?" + urlencode(search_query), headers=search_headers)
        # pprint.pprint(json.loads(response.content)["tracks"])

        djr.search_for_song("money pink floyd", access_token)

        test_server.serve_forever()

        #requests.get("https://api.spotify.com/v1/tracks/")

        # test_server.serve_forever()
        # new_dj = djr.DJ(access_token, test_server)
    else:
        print("Error code: " + auth_response.status_code)
