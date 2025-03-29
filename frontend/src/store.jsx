import { create } from "zustand";
import { addEdge, applyEdgeChanges, applyNodeChanges } from "@xyflow/react";

import { layout } from "./utils/graph.js";

const initialPlanState = {
  id: "",
  query: "",
  timestamp: 0,
  nodes: [],
  edges: [],
};

export const usePlanStore = create((set, get) => ({
  ...initialPlanState,

  initializePlan: () => {
    set(initialPlanState);
  },
  getNextNodeId: () => {
    const nodes = get().nodes;
    const maxId =
      nodes.length > 0
        ? Math.max(...nodes.map((node) => parseInt(node.id)))
        : -1;
    return (maxId + 1).toString();
  },

  onNodesChange: (changes) => {
    changes.map((change) => {
      if (change.type == "add") {
        console.log("onNodesChange", change);
      } else if (change.type == "replace") {
        console.log("onNodesChange", change);
      } else if (change.type == "remove") {
        console.log("onNodesChange", change);
      }
    });
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  onEdgesChange: (changes) => {
    console.log("onEdgesChange", changes);
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  // onConnect: (connection) => {
  //   console.log("onConnect", connection);
  //   const edge = {
  //     ...connection,
  //     id: `e_${connection.source}-${connection.target}_('${connection.sourceHandle}', '${connection.targetHandle}')`,
  //     data: {
  //       src_node: parseInt(connection.source),
  //       src_output: connection.sourceHandle,
  //       dest_node: parseInt(connection.target),
  //       dest_input: connection.targetHandle,
  //       plan_status: "MODIFIED",
  //     },
  //   };
  //   set({
  //     edges: addEdge(edge, get().edges),
  //   });
  // },

  setQuery: (query) => {
    set({ query });
  },
  applyLayout: () => {
    const { nodes, edges } = layout(get().nodes, get().edges);
    set({ nodes, edges });
  },
  setPlan: (plan) => {
    set({ ...plan });
  },
  setPlanLayout: (plan) => {
    const { nodes, edges } = layout(plan.nodes, plan.edges);
    set({ ...plan, nodes, edges });
  },
  setNodes: (nodes) => {
    set({ nodes });
  },
  addNode: (node) => {
    set({ nodes: [...get().nodes, node] });
  },
  removeNode: (nodeId) => {
    set({ nodes: get().nodes.filter((node) => node.id !== nodeId) });
  },
  updateNodeData: (nodeId, nodeData) => {
    set({
      nodes: get().nodes.map((node) => {
        if (node.id === nodeId) {
          return { ...node, data: { ...nodeData } };
        }
        return node;
      }),
    });
  },
  doesIOVarExist: (nodeId, varType, val) => {
    const node = get().nodes.find((node) => node.id == nodeId);
    if (varType == "input") {
      return node.data.input.some((d) => d[0] == val[0]);
    } else if (varType == "output") {
      return node.data.output.includes(val);
    }
    return true;
  },
  setEdges: (edges) => {
    set({ edges });
  },
  addEdge: (edge) => {
    set({ edges: addEdge(edge, get().edges) });
  },
  removeEdge: (edgeID) => {
    set({ edges: get().edges.filter((edge) => edge.id !== edgeID) });
  },
  // removeIncomingEdges: (nodeId, handleId) => {
  //   set({
  //     edges: get().edges.filter(
  //       (edge) => edge.target !== nodeId || edge.targetHandle !== handleId
  //     ),
  //   });
  // },
  // removeOutgoingEdges: (nodeId, handleId) => {
  //   set({
  //     edges: get().edges.filter(
  //       (edge) => edge.source !== nodeId || edge.sourceHandle !== handleId
  //     ),
  //   });
  // },
  removeConnectedEdges: (nodeId, varType, handleId) => {
    set({
      edges: get().edges.filter((edge) => {
        if (varType == "input") {
          return edge.target !== nodeId || edge.targetHandle !== handleId;
        } else if (varType == "output") {
          return edge.source !== nodeId || edge.sourceHandle !== handleId;
        } else {
          return true;
        }
      }),
    });
  },
  // updateIncomingEdges: (nodeId, idx, handleId, newHandleId) => {
  //   set({
  //     nodes: get().nodes.map((node) => {
  //       if (node.id === nodeId) {
  //         return {
  //           ...node,
  //           data: {
  //             ...node.data,
  //             input: node.data.input.map((d, i) => {
  //               if (i == idx) {
  //                 return [newHandleId, d[1]];
  //               }
  //               return d;
  //             }),
  //             plan_status: "MODIFIED",
  //           },
  //         };
  //       }
  //       return node;
  //     }),
  //     edges: get().edges.map((edge) => {
  //       if (edge.target == nodeId && edge.targetHandle == handleId) {
  //         return {
  //           ...edge,
  //           id: `e_${edge.source}-${edge.target}_('${edge.sourceHandle}', '${newHandleId}')`,
  //           targetHandle: newHandleId,
  //           data: {
  //             ...edge.data,
  //             dest_input: newHandleId,
  //             plan_status: "MODIFIED",
  //           },
  //         };
  //       }
  //       return edge;
  //     }),
  //   });
  // },
  // updateOutgoingEdges: (nodeId, idx, handleId, newHandleId) => {
  //   set({
  //     nodes: get().nodes.map((node) => {
  //       if (node.id === nodeId) {
  //         return {
  //           ...node,
  //           data: {
  //             ...node.data,
  //             output: node.data.output.map((d, i) => {
  //               if (i == idx) {
  //                 return newHandleId;
  //               }
  //               return d;
  //             }),
  //             plan_status: "MODIFIED",
  //           },
  //         };
  //       }
  //       return node;
  //     }),
  //     edges: get().edges.map((edge) => {
  //       if (edge.source == nodeId && edge.sourceHandle == handleId) {
  //         return {
  //           ...edge,
  //           id: `e_${edge.source}_${edge.target}_('${newHandleId}', '${edge.targetHandle}')`,
  //           sourceHandle: newHandleId,
  //           data: {
  //             ...edge.data,
  //             src_output: newHandleId,
  //             plan_status: "MODIFIED",
  //           },
  //         };
  //       }
  //       return edge;
  //     }),
  //   });
  // },
  updateConnectedEdges: (nodeId, varType, idx, handleId, newHandleId) => {
    set({
      nodes: get().nodes.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              [varType]: node.data[varType].map((d, i) => {
                if (i == idx) {
                  return varType == "input" ? [newHandleId, d[1]] : newHandleId;
                }
                return d;
              }),
              plan_status: "MODIFIED",
            },
          };
        }
        return node;
      }),
      edges: get().edges.map((edge) => {
        const sourceOrTarget = varType == "input" ? "target" : "source";
        const sourceOrTargetHandle =
          varType == "input" ? "targetHandle" : "sourceHandle";
        const destInOrSrcOut = varType == "input" ? "dest_input" : "src_output";
        const newId =
          varType == "input"
            ? `e_${edge.source}-${edge.target}_('${edge.sourceHandle}', '${newHandleId}')`
            : `e_${edge.source}_${edge.target}_('${newHandleId}', '${edge.targetHandle}')`;
        if (
          edge[sourceOrTarget] == nodeId &&
          edge[sourceOrTargetHandle] == handleId
        ) {
          return {
            ...edge,
            id: newId,
            [sourceOrTargetHandle]: newHandleId,
            data: {
              ...edge.data,
              [destInOrSrcOut]: newHandleId,
              plan_status: "MODIFIED",
            },
          };
        }
        return edge;
      }),
    });
  },
}));
