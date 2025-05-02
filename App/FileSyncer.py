import os
import sys
import hashlib
import requests
import json

def CalculateMd5(FilePath):
    """计算文件的MD5哈希值"""
    if not os.path.exists(FilePath):
        return None
    
    with open(FilePath, 'rb') as File:
        Md5Hash = hashlib.md5()
        for Chunk in iter(lambda: File.read(4096), b''):
            Md5Hash.update(Chunk)
        return Md5Hash.hexdigest()

def DisplayProgressBar(Iteration, Total, BarLength=50):
    """在命令行显示进度条"""
    Progress = float(Iteration) / float(Total)
    Arrow = '=' * int(round(Progress * BarLength) - 1) + '>'
    Spaces = ' ' * (BarLength - len(Arrow))
    
    sys.stdout.write(f"\r进度: [{Arrow}{Spaces}] {int(Progress * 100)}%")
    sys.stdout.flush()
    
    if Iteration == Total:
        sys.stdout.write('\n')

def DownloadFileWithProgress(Url, FilePath):
    """下载文件并显示进度条"""
    try:
        Response = requests.get(Url, stream=True)
        if Response.status_code != 200:
            return None, f"HTTP状态码 {Response.status_code}"
        
        # 获取文件大小
        TotalSize = int(Response.headers.get('content-length', 0))
        
        # 如果无法获取大小，直接下载
        if TotalSize == 0:
            return Response.content, None
        
        # 分块下载，显示进度
        DownloadedSize = 0
        Chunks = []
        
        for Data in Response.iter_content(chunk_size=4096):
            DownloadedSize += len(Data)
            Chunks.append(Data)
            DisplayProgressBar(DownloadedSize, TotalSize)
            
        return b''.join(Chunks), None
    except requests.exceptions.RequestException as Error:
        return None, str(Error)

def LoadConfigFromUrl(ConfigUrl):
    """从URL加载配置文件"""
    try:
        print(f"正在从 {ConfigUrl} 下载配置...")
        Response = requests.get(ConfigUrl)
        if Response.status_code != 200:
            return None, f"无法下载配置文件，HTTP状态码: {Response.status_code}"
        
        # 优先使用KV格式解析（每行一个键值对，格式为key = value）
        ConfigData = {}
        Lines = Response.text.strip().split('\n')
        
        # 过滤掉空行和注释行
        ValidLines = [Line for Line in Lines if Line.strip() and not Line.strip().startswith('#')]
        
        for Line in ValidLines:
            Parts = Line.split('=', 1)
            if len(Parts) == 2:
                Key = Parts[0].strip()
                Value = Parts[1].strip()
                ConfigData[Key] = Value
        
        # 如果成功解析为KV格式，直接返回
        if ConfigData:
            print("已成功使用键值对格式解析配置文件")
            return ConfigData, None
        
        # 如果KV格式解析失败，尝试JSON格式
        try:
            print("键值对格式解析失败，尝试使用JSON格式...")
            ConfigData = json.loads(Response.text)
            print("已成功使用JSON格式解析配置文件")
            return ConfigData, None
        except json.JSONDecodeError:
            return None, "配置文件格式无法识别，既不是有效的键值对格式也不是有效的JSON格式"
            
    except requests.exceptions.RequestException as Error:
        return None, f"下载配置出错: {str(Error)}"
    except Exception as Error:
        return None, f"处理配置文件时出错: {str(Error)}"

def SyncFiles(FileMapping):
    """
    同步本地文件与远程文件
    
    参数:
        FileMapping: 字典，键是本地文件路径，值是远程URL
    """
    TotalFiles = len(FileMapping)
    CurrentFile = 0
    
    print(f"开始同步 {TotalFiles} 个文件...")
    
    for LocalPath, RemoteUrl in FileMapping.items():
        CurrentFile += 1
        try:
            print(f"\n[{CurrentFile}/{TotalFiles}] 正在处理: {LocalPath}")
            
            # 创建目录（如果不存在）
            Directory = os.path.dirname(LocalPath)
            if Directory and not os.path.exists(Directory):
                os.makedirs(Directory, exist_ok=True)
            
            # 下载远程文件并显示进度
            print(f"下载中: {RemoteUrl}")
            RemoteData, Error = DownloadFileWithProgress(RemoteUrl, LocalPath)
            
            if Error or RemoteData is None:
                print(f"下载失败: {LocalPath} - {Error}")
                continue
            
            # 计算远程文件的MD5
            RemoteMd5 = hashlib.md5(RemoteData).hexdigest()
            
            # 计算本地文件的MD5（如果存在）
            LocalMd5 = CalculateMd5(LocalPath)
            
            # 如果本地文件不存在或MD5不同，则更新文件
            if LocalMd5 is None:
                with open(LocalPath, 'wb') as File:
                    File.write(RemoteData)
                print(f"已创建: {LocalPath}")
            elif LocalMd5 != RemoteMd5:
                with open(LocalPath, 'wb') as File:
                    File.write(RemoteData)
                print(f"已更新: {LocalPath}")
            else:
                print(f"已是最新: {LocalPath}")
                
        except IOError as Error:
            print(f"文件操作出错: {LocalPath} - {str(Error)}")
        except Exception as Error:
            print(f"处理时发生未知错误: {LocalPath} - {str(Error)}")
    
    print(f"\n同步完成。总计: {TotalFiles} 个文件")
