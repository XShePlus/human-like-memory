import json, os, tempfile

class Tools():
    # 安全读取json，文件不存在或解析失败返回默认值
    def read_json(self, filepath, default=[]):
        if not os.path.exists(filepath):
            return default

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default

    # 安全写入json，先写临时文件再原子替换
    def write_json(self, filepath, data, indent=2, ensure_ascii=False):
        # 确保目录存在
        dir_path = os.path.dirname(os.path.abspath(filepath))
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # 写临时文件
        fd, temppath = tempfile.mkstemp(
            suffix='.json',
            prefix='tmp_',
            dir=dir_path or '.'
        )

        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
            # 原子替换原文件
            os.replace(temppath, filepath)
        except Exception:
            # 失败时清理临时文件
            if os.path.exists(temppath):
                os.unlink(temppath)
            raise
