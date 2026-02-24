import urllib.parse
import urllib.request
import os
import random
from calculate_hash import calculate_hash
from parser import bdecode, bencode

def get_peers(file_path, port=8080, max_peers=50):
    with open(file_path,'rb') as f:
        data=f.read()
    decoded=bdecode(data)

    if b'announce' not in decoded:
        raise ValueError("File is missing 'announce' key")

    info=decoded[b'info']    
    url_announce=decoded[b'announce'].decode('utf-8')
    info_hash=calculate_hash(file_path)

    if b'length' in info:
        left=info[b'length']
    elif b'files' in info:
        left=sum(f[b'length'] for f in info[b'files'])
    else:
        raise ValueError("Invalid info dict missing length or files")
    
    peer_id_prefix=b'-PY0001-'
    peer_id=peer_id_prefix+os.urandom(20-len(peer_id_prefix))

    params={
        'info_hash':info_hash,
        'peer_id':peer_id,
        "port":port,
        'upload':0,
        'download':0,
        'left':left,
        'compact':1,
        'event':'started',
        'max_peers':max_peers,
    }

    query_parts=[]
    for key,val in params.items():
        if isinstance(val,bytes):
            enc_val=urllib.parse.quote(val,safe='')
            query_parts.append(f"{key}={enc_val}")
        else:
            query_parts.append(f"{key}={urllib.parse.quote(str(val),safe='')}")

    query_string='&'.join(query_parts)

    if '?' in url_announce:
        full_url=url_announce+'&'+query_string
    else:
        full_url=url_announce+'?'+query_string

    print(f"Full url: {full_url}")
    print(f"Announce url: {url_announce}")

    req=urllib.request.Request(full_url)
    req.add_header('User-Agent','Python-ProtoTorrent-Client/1.0')

    try:
        with urllib.request.urlopen(req, timeout=10) as responce:
            traker_data=responce.read()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='ignore')
        raise ValueError(f"Tracker returned error: {e.code} - {error_body}")

    print(f"Data retrived from tracker: {traker_data}")
    traker_data_decoded=bdecode(traker_data)

    if b'failure reason' in traker_data_decoded:
        failure = traker_data_decoded[b'failure reason'].decode('utf-8')
        raise ValueError(f"Tracker failure: {failure}")
    
    if b'peers' not in traker_data_decoded:
        raise ValueError("Tracker missing the peers key")
    
    peers_data=traker_data_decoded[b'peers']

    peers=[]
    if isinstance(peers_data,bytes):
        if(len(peers_data)%6!=0): # 4 + 2 bytes per peer
            raise ValueError("Invalid compact peers format")
        
        for i in range(0, len(peers_data), 6):
            ip_bytes = peers_data[i:i+4]
            port_bytes = peers_data[i+4:i+6]
            ip = '.'.join(map(str, ip_bytes))
            port = int.from_bytes(port_bytes, 'big')
            peers.append((ip, port))

    elif isinstance(peers_data,list):
        for new_dict in peers_data:
            ip=new_dict[b'ip'].decode('utf-8')
            port=new_dict[b'port']
            peers.append((ip,port))

    else:
        raise ValueError("Peer format unknown")
    
    return peers


if __name__ == "__main__":
    try:
        peers = get_peers('../torrent/kali-linux-2025.4-live-amd64.iso.torrent')
        print(f"\nFound {len(peers)} peers from tracker:")
        for ip, port in peers[:10]:
            print(f"  {ip}:{port}")
        if len(peers) > 10:
            print(f"  ... and {len(peers) - 10} more")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()