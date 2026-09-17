from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Pipeline, Document
from app.core.security import get_current_user_token
from app.services.pipeline_engine import pipeline_engine
from app.api.v1.tools import get_decrypted_pdf_buffer, save_modified_pdf
from app.schemas.all_schemas import PipelineCreate, PipelineExecuteRequest, PipelineNode, PipelineEdge, DocumentResponse

router = APIRouter()

# Default starter enterprise pipeline templates
ENTERPRISE_TEMPLATES = [
    {
        "name": "Enterprise Legal Sanitizer",
        "description": "Auto OCR -> Bates Stamp -> Deep Redaction -> AES-256 Lock",
        "nodes": [
            {"id": "n1", "type": "ocr", "position": {"x": 100, "y": 150}, "data": {"language": "eng"}},
            {"id": "n2", "type": "bates", "position": {"x": 320, "y": 150}, "data": {"prefix": "CASE-2026-"}},
            {"id": "n3", "type": "redact", "position": {"x": 540, "y": 150}, "data": {"burn_raster_pixels": True}},
            {"id": "n4", "type": "encrypt", "position": {"x": 760, "y": 150}, "data": {"password": "EnterpriseSecretPass!"}}
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
            {"id": "e3", "source": "n3", "target": "n4"}
        ]
    },
    {
        "name": "Cloud Storage Archival Optimizer",
        "description": "Grayscale -> Extreme Compression -> Linearize Web PDF",
        "nodes": [
            {"id": "n1", "type": "grayscale", "position": {"x": 100, "y": 150}, "data": {}},
            {"id": "n2", "type": "compress", "position": {"x": 350, "y": 150}, "data": {"quality": "high"}},
            {"id": "n3", "type": "watermark", "position": {"x": 600, "y": 150}, "data": {"text": "ARCHIVED COPY", "opacity": 0.2}}
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"}
        ]
    }
]

@router.post("/create")
async def create_pipeline(
    payload: PipelineCreate,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    nodes_raw = [n.model_dump() for n in payload.nodes]
    edges_raw = [e.model_dump() for e in payload.edges]

    pipeline = Pipeline(
        user_id=user_id,
        name=payload.name,
        description=payload.description,
        graph_definition={"nodes": nodes_raw, "edges": edges_raw},
        is_template=payload.is_template
    )
    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)

    return {
        "id": pipeline.id,
        "name": pipeline.name,
        "nodes_count": len(payload.nodes),
        "edges_count": len(payload.edges)
    }

@router.get("/templates")
async def get_templates():
    return ENTERPRISE_TEMPLATES

@router.get("/list")
async def list_pipelines(
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    stmt = select(Pipeline).where(Pipeline.user_id == user_id).order_by(Pipeline.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/execute", response_model=DocumentResponse)
async def execute_pipeline(
    payload: PipelineExecuteRequest,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    
    # 1. Fetch Pipeline
    stmt = select(Pipeline).where(Pipeline.id == payload.pipeline_id, Pipeline.user_id == user_id)
    res = await db.execute(stmt)
    pipe = res.scalars().first()
    if not pipe:
        raise HTTPException(status_code=404, detail="Pipeline definition not found")

    # 2. Fetch input document
    orig_doc, buf = await get_decrypted_pdf_buffer(payload.input_document_id, user_id, db)

    # 3. Parse nodes & edges
    nodes = [PipelineNode(**n) for n in pipe.graph_definition.get("nodes", [])]
    edges = [PipelineEdge(**e) for e in pipe.graph_definition.get("edges", [])]

    # 4. Execute Pipeline DAG
    res_dict = await pipeline_engine.execute_pipeline(nodes, edges, buf)
    final_buf = res_dict["final_buffer"]

    return await save_modified_pdf(
        user_id,
        f"piped_{orig_doc.original_filename}",
        final_buf,
        db
    )
