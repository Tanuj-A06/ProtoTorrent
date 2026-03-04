import fs from 'fs'
import bencode from 'bencode'
import crypto from 'crypto'

const open = (file_path) => {
    return bencode.decode(fs.readFileSync(file_path))
};

const infohash = (torrent) =>{
    return crypto.createHash('sha1').update(bencode.encode(torrent.info)).digest('hex');
};

const torr=open("./torrent/kali-linux-2025.4-live-amd64.iso.torrent")
console.log(infohash(torr));


const size = (file_path) =>{
    let total=0;

    if(file_path.info.length !== undefined) total=file_path.info.length;
    else{
        total=file_path.info.files.map(file=>file.length).reduce((sum,len)=> sum+len,0);
    }

    const buffer=Buffer.alloc(8);
    buffer.writeBigInt64BE(BigInt(total));
    return buffer;
};

const sizes=open("./torrent/kali-linux-2025.4-live-amd64.iso.torrent");
console.log("Size: ", size(sizes).readBigInt64BE())