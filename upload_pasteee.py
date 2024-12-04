import os
import json
import base64
from pasteee import Paste
import requests

def split_upload(in_file:str, out_path:str, max_file_size:int = 1024 * 1024):
    """
    大きなファイルを分割してアップロードする

    Parameters
    ----------
    in_file : str
        分割するファイルのパス
    out_path : str
        分割されたファイルを置くディレクトリーのパス
    max_file_size : int
        分割されたファイルの最大サイズ（byte）。
        1024 * 1024 = 1048576 byte = 1MB がデフォルト
    """
    urls = []
    basename = os.path.basename(in_file)
    sp = basename.rfind(".")
    name = basename[:sp]
    ext = basename[sp:]
    with open(in_file, "rb") as f:
        i = 0
        while True:
            content = f.read(int(max_file_size / 4 * 3))
            if not content:
                break
            content_b64 = base64.b64encode(content).decode("utf-8")
            paste = Paste(content_b64, private=False, desc=f"tweetdata_b64_{i}", views=15)
            urls.append(paste['download'])
            i += 1
    with open(f"{out_path}\\{name}_chunk_downloads.json", "w", encoding="utf-8") as f:
        out = {
            "name": name,
            "ext": ext,
            "chunks": i,
            "urls": urls
        }
        json.dump(out, f)

def merge_download(in_path:str, out_path:str, out_name:str = ""):
    """
    小さなファイルに分割された大きなファイルを1つにまとめる

    Parameters
    ----------
    in_path : str
        ダウンロードに使うjsonファイルのパス
    out_path : str
        まとめられたファイル出力するディレクトリのパス
    out_name : str
        まとめられたファイルの名前
        デフォルトは元のファイル名
    """
    if not os.path.isfile(f"{in_path}"):
        raise Exception("path is not available")
    with open(f"{in_path}", "r") as f:
        data = json.load(f)
        name = data["name"]
        ext = data["ext"]
        chunks = data["chunks"]
        urls = data["urls"]
        if not out_name:
            out_name = name
    with open(f"{out_path}\\{out_name}{ext}", "wb") as out_f:
        for i in range(chunks):
            res = requests.get(urls[i])
            content = base64.b64decode(res.content)
            out_f.write(content)