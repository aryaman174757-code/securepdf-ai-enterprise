import React from "react";
import { PDF_TOOLS_CATALOG } from "@/lib/toolsCatalog";
import { ToolWorkbenchClient } from "./ToolWorkbenchClient";

export function generateStaticParams() {
  return PDF_TOOLS_CATALOG.map((tool) => ({
    toolId: tool.id,
  }));
}

export default async function ToolWorkbenchPage({
  params,
}: {
  params: Promise<{ toolId: string }>;
}) {
  const resolvedParams = await params;
  return <ToolWorkbenchClient toolId={resolvedParams.toolId} />;
}
