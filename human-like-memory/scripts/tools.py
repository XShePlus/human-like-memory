import json,os,tempfile

class Tools():
    #安全读取json
    def read_json(self, filepath, default=[]) -> dict:
        if not os.path.exists(filepath):
            return default
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default

    #安全写入json
    def write_json(self, filepath, data, indent=2, ensure_ascii=False):
        
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        fd, temppath = tempfile.mkstemp(
            suffix='.json',
            prefix='tmp_',
            dir=os.path.dirname(filepath) or '.'
        )
        
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
            os.replace(temppath, filepath)
        except Exception:
            if os.path.exists(temppath):
                os.unlink(temppath)
            raise