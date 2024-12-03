import base64
import os
import json

def split_file(in_file:str, out_path:str, max_file_size:int = 1024 * 1024 * 20):
    """
    大きなファイルを小さなファイルに分割する

    Parameters
    ----------
    in_file : str
        分割するファイルのパス
    out_path : str
        分割されたファイルを置くディレクトリーのパス
    max_file_size : int
        分割されたファイルの最大サイズ（byte）。
        1024 * 1024 * 10 = 10485760 byte = 20MB がデフォルト
    """
    basename = os.path.basename(in_file)
    sp = basename.rfind(".")
    name = basename[:sp]
    ext = basename[sp:]
    if os.path.exists(f"{out_path}\\{name}_chunks"):
        raise Exception("chunks folder already exists")
    os.mkdir(f"{out_path}\\{name}_chunks")
    with open(in_file, "rb") as f:
        i = 0
        while True:
            content = f.read(max_file_size)
            if not content:
                break
            content_str = base64.b64encode(content)
            with open(f"{out_path}\\{name}_chunks\\{name}_chunk_{i}.txt", "wb") as out_f:
                out_f.write(content_str)
            i += 1
    with open(f"{out_path}\\{name}_chunks\\index.json", "w", encoding="utf-8") as f:
        out = {
            "name": name,
            "ext": ext,
            "chunks": i
        }
        json.dump(out, f)

def merge_files(in_path:str, out_path:str, out_name:str = ""):
    """
    小さなファイルに分割された大きなファイルを1つにまとめる

    Parameters
    ----------
    in_path : str
        分割されたファイルを置くディレクトリーのパス
    out_path : str
        まとめられたファイル出力するディレクトリのパス
    out_name : str
        まとめられたファイルの名前
        デフォルトは元のファイル名
    """
    if not os.path.isfile(f"{in_path}\\index.json"):
        raise Exception("index.json not found")
    with open(f"{in_path}\\index.json", "r") as f:
        data = json.load(f)
        name = data["name"]
        ext = data["ext"]
        chunks = data["chunks"]
        if not out_name:
            out_name = name
    with open(f"{out_path}\\{out_name}{ext}", "wb") as out_f:
        for i in range(chunks):
            with open(f"{in_path}\\{name}_chunk_{i}.txt", "rb") as f:
                content = base64.b64decode(f.read())
                out_f.write(content)