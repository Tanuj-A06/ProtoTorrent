import pprint

def int_parse(data,i): # Example: b'i123e'
    assert data[i]==ord('i')
    i+=1
    j=data.index(b'e',i)
    result=int(data[i:j].decode())
    return result,j+1

def str_parse(data,i): #Example: b'12:Middle Earth'
    j=data.index(b':',i)
    length=int(data[i:j])
    j+=1
    s=data[j:j+length]
    return s,j+length

def list_parse(data,i): # Lists start with a 'l' and end with a 'e'
    assert data[i]==ord('l')
    i+=1
    arr=[]
    while i<len(data) and data[i]!=ord('e'):
        result,i=parse_any(data,i)
        arr.append(result)
    return arr,i+1

def dict_parse(data,i):
    assert data[i]==ord('d')
    i+=1
    d={}
    while i<len(data) and data[i]!=ord('e'):
        key,i=str_parse(data,i)
        val,i=parse_any(data,i)
        d[key]=val
    return d,i+1

def parse_any(data,i):
    if(data[i]==ord('i')):
        return int_parse(data,i)
    elif(data[i]==ord('l')):
        return list_parse(data,i)
    elif(data[i]==ord('d')):
        return dict_parse(data,i)
    elif(chr(data[i]).isdigit()): # this is because in torrent files a string is given by (int:<STR>) so if data[i] is number then the appending is a string
        return str_parse(data,i)
    else:
        raise ValueError(f"Invalid bencode at {i}: {chr(data[i])}")


def bdecode(data):
    if not isinstance(data, bytes):
        raise ValueError("Input must be a byte string")
    if not data:
        raise ValueError("Empty input")
    
    result, index = parse_any(data, 0)
    if index < len(data):
        raise ValueError(f"Extra data after parsing at index {index}")
    return result
    # result=""
    # return result

def bencode(data):
    if isinstance(data,int):
        return b'i'+str(data).encode()+b'e'
    elif isinstance(data,str):
        data=data.encode('utf-8')
        return str(len(data)).encode()+b':'+data
    elif isinstance(data,bytes): 
        return str(len(data)).encode()+b':'+data
    elif isinstance(data,list):
        result=[b'l']
        for item in data:
            result.append(bencode(item))
        result.append(b'e')
        return b''.join(result)
    elif isinstance(data,dict):
        result=[b'd']
        for key in sorted(data.keys):
            if not isinstance(key, bytes):
                key = key.encode('utf-8')  # Convert string keys to bytes
            result.append(bencode(key))
            result.append(bencode(data[key]))
        result.append(b'e')
        return b''.join(result)
    else:
        return ValueError(f"Unsupported type of bencoding {type(data)}")

with open('../torrent/kali-linux-2025.4-live-amd64.iso.torrent','rb') as torrent:
    data=torrent.read()

decoded=bdecode(data)
pprint.pprint(decoded)