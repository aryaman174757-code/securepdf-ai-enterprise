"use client";

import React from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { PipelineCanvas } from "@/components/pipeline-builder/PipelineCanvas";

export default function PipelinesPage() {
  return (
    <div className="flex flex-1 overflow-hidden">
      <Sidebar />

      <div className="flex-1 overflow-y-auto p-8">
        <PipelineCanvas />
      </div>
    </div>
  );
}
