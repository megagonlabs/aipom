import dagre from "@dagrejs/dagre";

// initial width, height
const nodeWidth = 400;
const nodeHeight = 200;
const taskNodeHeight = 400;

const g = new dagre.graphlib.Graph();
g.setDefaultEdgeLabel(() => ({}));

export const layout = (nodes, edges, direction = "LR") => {
  g.setGraph({ rankdir: direction });
  nodes.forEach((node) =>
    g.setNode(node.id, {
      width: node.measured ? node.measured.width : node.type == nodeWidth,
      height: node.measured ? node.measured.height : node.type == "_task" ? taskNodeHeight : nodeHeight,
    })
  );
  edges.forEach((edge) => g.setEdge(edge.source, edge.target));
  dagre.layout(g);

  return {
    edges,
    nodes: nodes.map((node) => {
      const { x, y, width, height } = g.node(node.id);
      return {
        ...node,
        position: { x: x - width / 2, y: y - height / 2 },
      };
    }),
  };
};
