import hashlib
import pprint
from parser import bencode,bdecode

def calculate_hash(file_path):
    with open(file_path,'rb') as f:
        data=f.read()
    
    decode=bdecode(data)

    if b'info' not in decode:
        raise ValueError("The file dosent contain the info dict")
    info_dict=decode[b'info']

    info_encoded=bencode(info_dict)
    # why not sha256, cauze The BitTorrent protocol requires SHA-1 for the info hash. Trackers and peers identify torrents by their 20-byte SHA-1 hash
    # Using sha256 the other things will fail
    info_hash=hashlib.sha1(info_encoded).digest()

    return info_hash

try:
    with open('../torrent/kali-linux-2025.4-live-amd64.iso.torrent','rb') as torrent:
        data=torrent.read()

    info_hash=calculate_hash(data)
    print("Hash hex: ",info_hash.hex())
    print("Hash bytes: ",info_hash)

except FileNotFoundError:
    print(f"Error: The input file dosen't exist")

except ValueError as e:
    print(f"Error: {e}")