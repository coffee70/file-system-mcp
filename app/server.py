import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .models import (
    ListDirRequest,
    ReadFileRequest,
    ReadFilesRequest,
    RipgrepSearchRequest,
    AstGrepSearchRequest,
    ProposePatchRequest,
    ApplyPatchRequest,
    GetRepoMapRequest,
    WriteFileRequest,
)
from .tools.list_dir import handle_list_dir
from .tools.read_file import handle_read_file
from .tools.read_files import handle_read_files
from .tools.ripgrep_search import handle_ripgrep_search
from .tools.ast_grep_search import handle_ast_grep_search
from .tools.propose_patch import handle_propose_patch
from .tools.apply_patch import handle_apply_patch
from .tools.get_repo_map import handle_get_repo_map
from .tools.write_file import handle_write_file

app = FastAPI(title="MCP Code Assistant")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tools/list_dir")
def list_dir(req: ListDirRequest):
    try:
        result = handle_list_dir(req)
        return JSONResponse(content=json.loads(result.model_dump_json()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/read_file")
def read_file(req: ReadFileRequest):
    try:
        result = handle_read_file(req)
        return JSONResponse(content=json.loads(result.model_dump_json()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/read_files")
def read_files(req: ReadFilesRequest):
    try:
        result = handle_read_files(req)
        return JSONResponse(content=json.loads(result.model_dump_json()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/ripgrep_search")
def ripgrep_search(req: RipgrepSearchRequest):
    try:
        result = handle_ripgrep_search(req)
        return JSONResponse(content=json.loads(result.model_dump_json()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/ast_grep_search")
def ast_grep_search(req: AstGrepSearchRequest):
    try:
        result = handle_ast_grep_search(req)
        return JSONResponse(content=json.loads(result.model_dump_json()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/propose_patch")
def propose_patch(req: ProposePatchRequest):
    try:
        result = handle_propose_patch(req)
        return JSONResponse(content=json.loads(result.model_dump_json()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/apply_patch")
def apply_patch(req: ApplyPatchRequest):
    try:
        result = handle_apply_patch(req)
        return JSONResponse(content=json.loads(result.model_dump_json()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/tools/get_repo_map")
def get_repo_map(req: GetRepoMapRequest):
    try:
        result = handle_get_repo_map(req)
        return JSONResponse(content=json.loads(result.model_dump_json()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/tools/write_file")
def write_file(req: WriteFileRequest):
    try:
        result = handle_write_file(req)
        return JSONResponse(content=json.loads(result.model_dump_json()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
