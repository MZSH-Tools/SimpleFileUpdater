from __future__ import annotations
import os, sys, time, hashlib, requests, tempfile, shutil
from typing import Dict, Tuple, Optional

CHUNK_SIZE: int = 8192          # 每次读取 8 KB
VERBOSE: bool = True            # True → 打印 DEBUG 日志
MAX_RETRY: int = 3              # 下载失败最多重试次数
RETRY_BACKOFF: float = 1.5      # 重试退避基数（秒）
HTTP_TIMEOUT: int = 30
USER_AGENT: str = "SimpleFileUpdater/1.0 (+https://github.com/MZSH-Tools/SimpleFileUpdater)"


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
    headers = {
        "Accept-Encoding": "identity",   # 关闭自动 gzip，确保 Content-Length 可用
        "User-Agent": USER_AGENT,
    }

    last_err: Optional[str] = None
    for attempt in range(1, MAX_RETRY + 1):
        tmp_path: Optional[str] = None
        try:
            with requests.get(url, stream=True, timeout=HTTP_TIMEOUT, headers=headers, allow_redirects=True) as r:
                r.raise_for_status()

                total = int(r.headers.get("Content-Length", 0))
                Debug(f"[尝试 {attempt}] Content-Length: {total}")
                Debug(f"[尝试 {attempt}] Content-Type  : {r.headers.get('Content-Type')}")

                downloaded = 0
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = tmp.name
                    for chunk in r.iter_content(CHUNK_SIZE):
                        if chunk:
                            tmp.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                PrintProgress(downloaded, total)

                if total and downloaded != total:
                    raise IOError(f"下载字节数与 Content-Length 不一致: {downloaded} / {total}")

                Debug(f"[尝试 {attempt}] Downloaded    : {downloaded}")
                return tmp_path, None
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            # 清理半成品
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            if attempt < MAX_RETRY:
                wait = RETRY_BACKOFF * attempt
                Debug(f"[尝试 {attempt}] 失败: {last_err} → {wait:.1f}s 后重试")
                time.sleep(wait)

    return None, last_err


# ─────────────────── 同步逻辑 ────────────────────
def SyncOne(local: str, url: str) -> bool:
    Debug(f"下载链接 → {url}")
    tmp_path, err = DownloadToTemp(url)
    if err:
        print(f"❌ 下载失败: {err}")
        return False

    abs_local = os.path.abspath(local)
    remote_md5 = FileMd5(tmp_path)
    local_md5  = FileMd5(abs_local)
    Debug(f"远端 MD5: {remote_md5}")
    Debug(f"本地 MD5: {local_md5 or 'None'}")

    if remote_md5 == local_md5:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        print("✔ 已是最新")
        return True

    parent = os.path.dirname(abs_local)
    if parent:
        os.makedirs(parent, exist_ok=True)

    try:
        shutil.move(tmp_path, abs_local)
    except Exception as e:
        print(f"❌ 写入失败: {type(e).__name__}: {e}")
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        return False

    print("🆕 已创建" if local_md5 is None else "🔄 已更新")
    return True


def SyncFiles(mapping: Dict[str, str]) -> int:
    """同步所有文件，返回失败条目数"""
    total = len(mapping)
    failed = 0
    print(f"\n开始同步，共 {total} 个文件\n")
    for idx, (local, url) in enumerate(mapping.items(), 1):
        print(f"[{idx}/{total}] 处理: {local}")
        try:
            if not SyncOne(local, url):
                failed += 1
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"❌ 未知错误: {type(e).__name__}: {e}")
            failed += 1

    if failed:
        print(f"\n⚠️  同步完成，{failed} 个文件失败")
    else:
        print("\n✅ 同步完成")
    return failed
