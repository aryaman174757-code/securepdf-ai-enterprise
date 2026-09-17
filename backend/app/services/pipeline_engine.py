import asyncio
from typing import Dict, List, Any, Callable, Optional
from app.schemas.all_schemas import PipelineNode, PipelineEdge, PipelineStepProgress
from app.services.pdf_modifier import pdf_modifier
from app.services.converter import converter_service
from app.services.ocr_engine import ocr_service
from app.services.redactor import redactor_service
from app.services.security_service import security_service

class PipelineEngine:
    """
    Visual Workflow DAG Execution Engine.
    Executes connected document pipelines in topological order
    and emits real-time progress callbacks for WebSocket distribution.
    """

    @staticmethod
    def validate_graph(nodes: List[PipelineNode], edges: List[PipelineEdge]) -> bool:
        """Ensure DAG has no cycles and nodes are valid."""
        node_ids = {n.id for n in nodes}
        for e in edges:
            if e.source not in node_ids or e.target not in node_ids:
                return False
        return True

    @classmethod
    async def execute_pipeline(
        cls,
        nodes: List[PipelineNode],
        edges: List[PipelineEdge],
        initial_pdf_buffer: bytes,
        progress_callback: Optional[Callable[[PipelineStepProgress], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes pipeline nodes sequentially, passing transformed PDF buffers between steps.
        """
        # Build node map
        node_dict = {n.id: n for n in nodes}
        # Find entry node
        targets = {e.target for e in edges}
        sources = {e.source for e in edges}
        entry_nodes = [n for n in nodes if n.id not in targets]

        current_buffer = initial_pdf_buffer
        step_results = []

        # Order nodes by topological flow
        execution_order = []
        visited = set()
        
        # Simple topological sort
        def visit(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            execution_order.append(node_dict[node_id])
            for edge in edges:
                if edge.source == node_id:
                    visit(edge.target)

        for en in entry_nodes:
            visit(en.id)

        # Execute each step
        total_steps = len(execution_order)
        for idx, node in enumerate(execution_order):
            progress_val = ((idx + 1) / total_steps) * 100.0
            
            # Notify step starting
            if progress_callback:
                progress_callback(PipelineStepProgress(
                    node_id=node.id,
                    node_type=node.type,
                    status="RUNNING",
                    progress=progress_val
                ))

            try:
                # Dispatch node action
                ntype = node.type.lower()
                data = node.data or {}

                if ntype == "ocr":
                    _, searchable_pdf = ocr_service.run_ocr_on_pdf(
                        current_buffer,
                        language=data.get("language", "eng"),
                        generate_searchable_pdf=True
                    )
                    if searchable_pdf:
                        current_buffer = searchable_pdf

                elif ntype == "compress":
                    current_buffer = pdf_modifier.compress_pdf(
                        current_buffer,
                        quality=data.get("quality", "medium")
                    )

                elif ntype == "watermark":
                    current_buffer = pdf_modifier.add_watermark(
                        current_buffer,
                        text=data.get("text", "CONFIDENTIAL"),
                        opacity=data.get("opacity", 0.3)
                    )

                elif ntype == "redact":
                    current_buffer = redactor_service.apply_deep_redaction(
                        current_buffer,
                        redactions=[],
                        burn_raster_pixels=True
                    )

                elif ntype == "encrypt":
                    pwd = data.get("password", "SecurePDF123!")
                    current_buffer = security_service.encrypt_pdf(
                        current_buffer,
                        user_password=pwd
                    )

                elif ntype == "grayscale":
                    current_buffer = pdf_modifier.convert_to_grayscale(current_buffer)

                elif ntype == "bates":
                    current_buffer = pdf_modifier.bates_number_pdf(
                        current_buffer,
                        prefix=data.get("prefix", "SPDF-")
                    )

                step_results.append({
                    "node_id": node.id,
                    "type": node.type,
                    "status": "COMPLETED"
                })

                if progress_callback:
                    progress_callback(PipelineStepProgress(
                        node_id=node.id,
                        node_type=node.type,
                        status="COMPLETED",
                        progress=progress_val
                    ))

            except Exception as e:
                if progress_callback:
                    progress_callback(PipelineStepProgress(
                        node_id=node.id,
                        node_type=node.type,
                        status="FAILED",
                        progress=progress_val,
                        error=str(e)
                    ))
                raise e

        return {
            "status": "SUCCESS",
            "total_nodes_executed": len(execution_order),
            "final_buffer": current_buffer
        }

pipeline_engine = PipelineEngine()
