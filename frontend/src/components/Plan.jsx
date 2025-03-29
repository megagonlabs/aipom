import { useCallback, useContext, useEffect } from "react";
import { useShallow } from "zustand/react/shallow";
import { Button, Card, EditableText, Tag, Tooltip } from "@blueprintjs/core";
import {
  Background,
  Controls,
  Panel,
  ReactFlow,
  ReactFlowProvider,
  useNodesInitialized,
  useReactFlow,
} from "@xyflow/react";

import { AppContext } from "../AppContext";
import { usePlanStore } from "../store";
import { InteractionType } from "../utils/constants.js";
import { layout } from "../utils/graph.js";

import { OutputNode, QueryNode, TaskNode } from "./Node";

import "@xyflow/react/dist/style.css";
import "react-edit-text/dist/index.css";

const nodeTypes = {
  _query: QueryNode,
  _task: TaskNode,
  _output: OutputNode,
};

const selector = (state) => ({
  query: state.query,
  nodes: state.nodes,
  edges: state.edges,
  onNodesChange: state.onNodesChange,
  onEdgesChange: state.onEdgesChange,
  setQuery: state.setQuery,
  applyLayout: state.applyLayout,
  setNodes: state.setNodes,
  addNode: state.addNode,
  removeNode: state.removeNode,
  setEdges: state.setEdges,
  addEdge: state.addEdge,
  removeEdge: state.removeEdge,
});

function PlanGraph() {
  const {
    query,
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    setQuery,
    applyLayout,
    setNodes,
    addNode,
    removeNode,
    setEdges,
    addEdge,
    removeEdge,
  } = usePlanStore(useShallow(selector));
  const { agentRegistry, rePlan, fixPlan, executeNode, sendInteraction, sendPlan } =
    useContext(AppContext);
  const nodesInitialized = useNodesInitialized();
  const { fitView } = useReactFlow();

  useEffect(() => {
    if (nodesInitialized) {
      const updatedPlan = layout(nodes, edges);
      setNodes([...updatedPlan.nodes]);
      setEdges([...updatedPlan.edges]);
      window.requestAnimationFrame(() => fitView());
    }
  }, [nodesInitialized]);

  const onLayout = () => {
    applyLayout();
    window.requestAnimationFrame(() => fitView());
  };

  const onExecuteAll = () => {
    sendPlan(nodes, edges);
    executeNode("all");
  };

  const onAddNode = useCallback(() => {
    const id = usePlanStore.getState().getNextNodeId();
    const defaultNodeData = {
      id: id,
      name: "fallback",
      task: "placeholder",
      input: [["placeholder", null]],
      output: ["placeholder"],
      params: { ...agentRegistry.configs["fallback"] },
      plan_status: "MODIFIED",
    };
    addNode({
      id: id,
      type: "_task",
      position: { x: 500, y: 500 },
      data: defaultNodeData,
    });
    sendInteraction({
      interaction: InteractionType.ADD_NODE,
      n: parseInt(id),
      n_attr: defaultNodeData,
    });
  }, [agentRegistry]);

  const onNodesDelete = useCallback((nodes) => {
    nodes.map((node) => {
      removeNode(node.id);
      sendInteraction({
        interaction: InteractionType.REMOVE_NODE,
        n: parseInt(node.id),
      });
    });
  }, []);

  const onAddEdge = useCallback(
    (connection) => {
      if (edges.filter((edge) => edge.target == connection.target && edge.targetHandle == connection.targetHandle).length > 0) {
        return;
      }
      const edge = {
        ...connection,
        id: `e_${connection.source}-${connection.target}_('${connection.sourceHandle}', '${connection.targetHandle}')`,
        data: {
          src_node: parseInt(connection.source),
          src_output: connection.sourceHandle,
          dest_node: parseInt(connection.target),
          dest_input: connection.targetHandle,
          plan_status: "MODIFIED",
        },
      };
      addEdge(edge);
      sendInteraction({
        interaction: InteractionType.ADD_EDGE,
        e_s: parseInt(edge.source),
        e_t: parseInt(edge.target),
        e_attr: edge.data,
      });
    },
    [edges]
  );

  const onEdgesDelete = useCallback((edges) => {
    edges.map((edge) => {
      removeEdge(edge.id);
      sendInteraction({
        interaction: InteractionType.REMOVE_EDGE,
        e_s: parseInt(edge.source),
        e_t: parseInt(edge.target),
        e_attr: edge.data,
      });
    });
  }, []);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      onInit={fitView}
      onNodesChange={onNodesChange}
      onNodesDelete={onNodesDelete}
      onEdgesChange={onEdgesChange}
      onEdgesDelete={onEdgesDelete}
      onConnect={onAddEdge}
      zoomOnScroll={false}
      fitView
    >
      <Controls position="bottom-right" />
      {/* <MiniMap /> */}
      <Background variant="dots" gap={15} size={1} />
      <Panel position="top-left">
        <Card compact style={{ width: 400 }}>
          <div className="cols-wrapper" style={{ display: "flex" }}>
            <Tag minimal>Q</Tag>
            <EditableText multiline={true} minLines={1} maxLines={2} style={{ width: "100%" }}
              placeholder="User query"
              value={query}
              onChange={(value) => setQuery(value)}
              onConfirm={(value) => setQuery(value)}
            />
          </div>
        </Card>
      </Panel>
      <Panel className="rows-wrapper" position="top-right">
        <div className="cols-wrapper">
          <Tooltip content="Auto-layout" placement="bottom">
            <Button icon="fullscreen" onClick={onLayout} />
          </Tooltip>
          {/* <Button icon="redo" onClick={onLayout} disabled /> */}
          {/* <Button icon="undo" onClick={onLayout} disabled /> */}
          <Tooltip content="Generate a new plan" placement="bottom">
            <Button icon="refresh" intent="primary" text="Re-plan" onClick={rePlan} />
          </Tooltip>
          <Tooltip content="Fix/complete plan with LLM" placement="bottom">
            <Button icon="build" intent="primary" text="Help!" onClick={fixPlan} />
          </Tooltip>
          <Tooltip content="Execute entire plan" placement="bottom-end">
            <Button icon="play" intent="success" text="Execute" onClick={onExecuteAll} />
          </Tooltip>
        </div>
        <div className="cols-wrapper" style={{ float: "right" }}>
          <Tooltip content="Add a node placeholder" placement="bottom-end">
            <Button icon="add" intent="primary" text="Add Task Node" onClick={onAddNode} />
          </Tooltip>
        </div>
      </Panel>
    </ReactFlow>
  );
}

export default function Plan() {
  return (
    <ReactFlowProvider>
      <PlanGraph />
    </ReactFlowProvider>
  );
}
