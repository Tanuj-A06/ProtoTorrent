import fs from 'fs'
import bencode from 'bencode'

const torrent=bencode.decode(
    fs.readFileSync("../torrent/kali-linux-2025.4-live-amd64.iso.torrent")
);

const announce=Buffer.from(torrent.announce).toString('utf-8');
console.log(announce);