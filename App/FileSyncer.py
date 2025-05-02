from __future__ import annotations
import os, sys, hashlib, requests, tempfile, shutil
from typing import Dict, Tuple, Optional

CHUNK_SIZE: int = 8192      # 每次读取 8 KB
VERBOSE: bool = True        # True → 打印 DEBUG 日志


# ──────────────────── 工具 ────────────────────
def Debug(msg: str) -> None:
    if VERBOSE:
        print(f"  [DEBUG] {msg}")


def FileMd5(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    h = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(block)
    return h.hexdigest()


def PrintProgress(done: int, total: int, width: int = 50) -> None:
    if total == 0:
        return
    ratio = done / total
    bar   = "=" * int(ratio * width - 1) + ">" if ratio < 1 else "=" * width
    sys.stdout.write(f"\r进度: [{bar:<{width}}] {ratio*100:6.2f}%")
    sys.stdout.flush()
    if done >= total:
        sys.stdout.write("\n")


# ─────────────────── 下载到临时文件 ──────────────────
def DownloadToTemp(url: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        headers = {"Accept-Encoding": "identity"}      # 关闭自动 gzip
        with requests.get(url, stream=True, timeout=30, headers=headers) as r:
            r.raise_for_status()

            total = int(r.headers.get("Content-Length", 0))
            Debug(f"Content-Length : {total}")
            Debug(f"Content-Type    : {r.headers.get('Content-Type')}")
            Debug(f"Transfer-Enc    : {r.headers.get('Transfer-Encoding', 'None')}")

            downloaded = 0
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in r.iter_content(CHUNK_SIZE):
                    if chunk:
                        tmp.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            PrintProgress(downloaded, total)
            Debug(f"Downloaded       : {downloaded}")
            return tmp.name, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


# ─────────────────── 配置加载（键值对） ──────────────────
def LoadConfigFromUrl(url: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    try:
        Debug(f"下载配置 → {url}")
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        mapping: Dict[str, str] = {}
        for line in resp.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = map(str.strip, line.split("=", 1))
                mapping[k] = v

        if mapping:
            Debug("配置解析成功：键值对格式")
            return mapping, None
        return None, "配置为空或无有效键值对"
    except Exception as e:
        return None, f"配置下载失败: {e}"


# ─────────────────── 同步逻辑 ────────────────────
def SyncOne(local: str, url: str) -> None:
    Debug(f"下载链接 → {url}")
    tmp_path, err = DownloadToTemp(url)
    if err:
        print(f"❌ 下载失败: {err}")
        return

    remote_md5 = FileMd5(tmp_path)
    local_md5  = FileMd5(local)
    Debug(f"远端 MD5: {remote_md5}")
    Debug(f"本地 MD5: {local_md5 or 'None'}")

    if remote_md5 == local_md5:
        os.remove(tmp_path)
        print("✔ 已是最新")
        return

    os.makedirs(os.path.dirname(local) or ".", exist_ok=True)
    shutil.move(tmp_path, local)
    print("🆕 已创建" if local_md5 is None else "🔄 已更新")


def SyncFiles(mapping: Dict[str, str]) -> None:
    total = len(mapping)
    print(f"\n开始同步，共 {total} 个文件\n")
    for idx, (local, url) in enumerate(mapping.items(), 1):
        print(f"[{idx}/{total}] 处理: {local}")
        try:
            SyncOne(local, url)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"❌ 未知错误: {e}")
    print("\n✅ 同步完成")
