from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import tempfile
import os
from utils.file_reader import read_pdf, read_word, read_excel, read_ppt, read_txt, convert_with_queue

app = FastAPI(title="文件内容读取服务")

class FileReadRequest(BaseModel):
    file_url: str

def get_file_type_from_url(url: str):
    url = url.lower()
    if url.endswith('.pdf'):
        return 'pdf'
    elif url.endswith('.docx') or url.endswith('.doc'):
        return 'word'
    elif url.endswith('.xlsx') or url.endswith('.xls'):
        return 'excel'
    elif url.endswith('.pptx') or url.endswith('.ppt'):
        return 'ppt'
    elif url.endswith('.txt'):
        return 'txt'
    else:
        return None

@app.post("/api/read-file")
async def read_file_api(req: FileReadRequest):
    try:
        file_type = get_file_type_from_url(req.file_url)
        if not file_type:
            raise HTTPException(status_code=400, detail="无法识别的文件类型")

        # 下载文件
        response = requests.get(req.file_url)
        response.raise_for_status()
        suffix = "." + file_type
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(response.content)
            file_path = tmp.name

        # 读取内容
        if file_type == "pdf":
            content = read_pdf(file_path)
        elif file_type == "word":
            # 如果是 .doc，先转 docx（用队列串行）
            if req.file_url.lower().endswith('.doc'):
                try:
                    new_path = convert_with_queue(file_path, "docx")
                    content = read_word(new_path)
                    os.remove(new_path)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"doc转docx失败: {str(e)}")
            else:
                content = read_word(file_path)
        elif file_type == "excel":
            content = read_excel(file_path)
        elif file_type == "ppt":
            # 如果是 .ppt，先转 pptx（用队列串行）
            if req.file_url.lower().endswith('.ppt'):
                try:
                    new_path = convert_with_queue(file_path, "pptx")
                    content = read_ppt(new_path)
                    os.remove(new_path)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"ppt转pptx失败: {str(e)}")
            else:
                content = read_ppt(file_path)
        elif file_type == "txt":
            content = read_txt(file_path)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        os.remove(file_path)
        return {"status": 200, "message": "读取成功", "content": content}
    except Exception as e:
        return {"status": 500, "message": f"读取失败: {str(e)}", "content": ""} 