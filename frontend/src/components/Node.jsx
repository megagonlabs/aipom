import { useContext, useEffect, useState } from "react";
import { EditText } from "react-edit-text";
import JsonView from "react18-json-view";
import {
  Button,
  Card,
  CardList,
  Collapse,
  Divider,
  FormGroup,
  HTMLSelect,
  InputGroup,
  Section,
  SectionCard,
  Tag,
  Tooltip,
} from "@blueprintjs/core";
import {
  Handle,
  Position,
  useEdges,
  useNodes,
  useReactFlow,
  useUpdateNodeInternals,
} from "@xyflow/react";

import { AppContext } from "../AppContext";
import { usePlanStore } from "../store";
import { InteractionType } from "../utils/constants.js";

import "react18-json-view/src/style.css";

function BaseNode(props) {
  const nodes = useNodes();
  const edges = useEdges();
  const { executeNode, sendPlan } = useContext(AppContext);

  const onExecuteNode = () => {
    sendPlan(nodes, edges);
    executeNode("single", parseInt(props.id));
  };

  return (
    <div className="node-wrapper">
      {/* {props.type !== "_query" && (
        <Handle type="target" position={Position.Top} />
      )} */}
      <Section
        icon={
          props.type == "_query"
            ? "person"
            : props.type == "_output"
              ? "bring-data"
              : "clean"
        }
        title={props.type.substring(1).toUpperCase() + " " + props.id}
        rightElement={
          <>
            {props.type == "_task" && props.status}
            {props.type !== "_output" && (
              <Tooltip content="Execute this node" placement="top">
                <Button
                  className="bp5-tiny"
                  icon="play"
                  intent={props.type == "_query" ? "primary" : "success"}
                  onClick={onExecuteNode}
                  disabled={props.type == "_query"}
                />
              </Tooltip>
            )}
          </>
        }
        style={{ overflow: "visible", cursor: "auto" }}
        compact
      >
        {props.children}
      </Section>
      {/* {props.type !== "_output" && (
        <Handle type="source" position={Position.Bottom} />
      )} */}
    </div>
  );
}

export function QueryNode({ id, type, data }) {
  const { updateNodeData } = useReactFlow();
  const onEdit = (params) => {
    console.log("---", params);
    // data.onChange(id, {...data, query: params.newValue});
    updateNodeData(id, { ...data, query: params.newValue });
    console.log(updateNodeData);
    // updateNodeData(id, {...data});
  };

  return (
    <BaseNode id={id} type={type} status={data.status}>
      <SectionCard>
        <JsonView
          src={data.query}
          editable={{ edit: true }}
          enableClipboard={false}
          onEdit={onEdit}
        />
      </SectionCard>
    </BaseNode>
  );
}

export function OutputNode({ id, type, data }) {
  return (
    <BaseNode id={id} type={type} status={data.status}>
      <SectionCard>
        <JsonView
          src={data.exec}
          editable={{ edit: true }}
          enableClipboard={false}
        />
      </SectionCard>
    </BaseNode>
  );
}

export function TaskNode({ id, type, data }) {
  const { agentRegistry, sendInteraction } = useContext(AppContext);
  const updateNodeData = usePlanStore((state) => state.updateNodeData);
  const removeConnectedEdges = usePlanStore((state) => state.removeConnectedEdges);
  const updateConnectedEdges = usePlanStore((state) => state.updateConnectedEdges);
  const doesIOVarExist = usePlanStore((state) => state.doesIOVarExist);
  const updateNodeInternals = useUpdateNodeInternals();
  const [isAgentConfigOpen, setIsAgentConfigOpen] = useState(false);
  const [newInputVar, setNewInputVar] = useState("");
  const [newOutputVar, setNewOutputVar] = useState("");

  const jsonViewConfig = {
    collapsed: 2,
    displayArrayIndex: false,
    displaySize: 2,
    editable: { edit: true },
    enableClipboard: false,
  };

  useEffect(() => {
    updateNodeInternals(id);
  }, [id, data, updateNodeInternals]);

  const updateNodeAgent = (e) => {
    e.stopPropagation();
    // console.log(e.target.value);
    const updatedNodeData = {
      ...data,
      name: e.currentTarget.value,
      params: { ...agentRegistry.configs[e.currentTarget.value] },
      plan_status: "MODIFIED",
    };
    // console.log(updatedNodeData);
    updateNodeData(id, updatedNodeData);
    sendInteraction({
      interaction: InteractionType.MODIFY_NODE,
      n: parseInt(id),
      n_attr: updatedNodeData,
    });
  };

  const modifyNode = (attr) => {
    return (params) => {
      let newValue;
      if (attr == "task") {
        newValue = params.newValue;
      } else if (attr == "input") {
        newValue = data.input.map((d) => [d[0], params.src[d[0]]]);
      } else {
        newValue = { ...params.src };
      }
      const updatedNodeData = {
        ...data,
        [attr]: newValue,
        plan_status: "MODIFIED",
      };
      updateNodeData(id, updatedNodeData);
      sendInteraction({
        interaction: InteractionType.MODIFY_NODE,
        n: parseInt(id),
        n_attr: updatedNodeData,
      });
    };
  };
  const updateNodeExec = (params) => {
    updateNodeData(id, { ...data, exec: params.src, exec_status: "MODIFIED" });
    const updatedExecAttr = params.depth == 1 ? params.indexOrName : params.parentPath[0];
    const updatedExecVal = params.depth == 1 ? params.newValue : params.src[params.parentPath[0]];
    sendInteraction({
      interaction: InteractionType.UPDATE_EXEC,
      n: parseInt(id),
      n_exec: params.src,
      n_exec_attr: updatedExecAttr,
      n_exec_attr_value: updatedExecVal,
    });
  };

  const onAddIOVar = (attr) => {
    return (e) => {
      e.stopPropagation();
      const newIOVar =
        attr == "input"
          ? [newInputVar, null]
          : attr == "output"
            ? newOutputVar
            : null;
      // console.log(newIOVar, doesIOVarExist(id, attr, newIOVar));
      if (newIOVar && !doesIOVarExist(id, attr, newIOVar)) {
        if (attr == "input") {
          setNewInputVar("");
        } else if (attr == "output") {
          setNewOutputVar("");
        }
        const updatedNodeData = {
          ...data,
          [attr]: [...data[attr], newIOVar],
          plan_status: "MODIFIED",
        };
        updateNodeData(id, updatedNodeData);
        sendInteraction({
          interaction: InteractionType.MODIFY_NODE,
          n: parseInt(id),
          n_attr: updatedNodeData,
        });
      }
    };
  };

  const removeIOVar = (attr) => {
    return (e, props) => {
      const removedHandle = props.children.props.defaultValue || props.children.props.value;
      removeConnectedEdges(id, attr, removedHandle);
      const newValue = data[attr].filter(
        (_, i) => i !== props.children.props.idx
      );
      const updatedNodeData = {
        ...data,
        [attr]: newValue,
        plan_status: "MODIFIED",
      };
      updateNodeData(id, updatedNodeData);
      const { edges } = usePlanStore.getState();
      sendInteraction({
        interaction: InteractionType.MODIFY_NODE_EDGES,
        n: parseInt(id),
        n_attr: updatedNodeData,
        edges: edges,
      });
    };
  };

  const onEditSaveIOVar = (attr, idx) => {
    return ({ value, previousValue }) => {
      updateConnectedEdges(id, attr, idx, previousValue, value);
      updateNodeInternals(id);
      const { nodes, edges } = usePlanStore.getState();
      sendInteraction({
        interaction: InteractionType.MODIFY_NODE_EDGES,
        n: parseInt(id),
        n_attr: nodes.find((node) => node.id == id).data,
        edges: edges,
      });
    };
  };

  return (
    <BaseNode id={id} type={type} status={data.exec_status}>
      {/* <SectionCard padded={false}> */}
      <CardList className="nodrag" bordered={false} compact>
        <Card style={{ display: "block" }}>
          <FormGroup label="Agent" inline fill>
            {/* <InputGroup id="text-input" placeholder="Placeholder text" /> */}
            <HTMLSelect
              value={data.name}
              options={agentRegistry.names}
              onChange={updateNodeAgent}
            />
            <Tooltip content="Agent configuration" placement="top">
              <Button
                icon="cog"
                // intent="primary"
                variant="minimal"
                aria-label="cog"
                onClick={() => setIsAgentConfigOpen(!isAgentConfigOpen)}
              />
            </Tooltip>
          </FormGroup>
          <Collapse isOpen={isAgentConfigOpen} keepChildrenMounted={true}>
            <JsonView
              {...jsonViewConfig}
              src={data.params}
              editable={{ add: true, edit: true, delete: true }}
              onAdd={modifyNode("params")}
              onEdit={modifyNode("params")}
              onDelete={modifyNode("params")}
            />
          </Collapse>
        </Card>
        <Card>
          <JsonView
            {...jsonViewConfig}
            className="task"
            src={data.task}
            onEdit={modifyNode("task")}
          />
        </Card>
        <Card>
          <JsonView
            {...jsonViewConfig}
            className="input"
            src={Object.fromEntries(data.input)}
            onEdit={modifyNode("input")}
          />
        </Card>
        {/* <Card>
          <JsonView
            {...jsonViewConfig}
            src={data.output}
            editable={{ add: true, edit: true, delete: true }}
            onAdd={modifyNode("output")}
            onEdit={modifyNode("output")}
            onDelete={modifyNode("output")}
          />
        </Card> */}
      </CardList>
      <Divider />
      <div className="node-input-output-wrapper nopan nodrag nowheel">
        <div className="node-input-list">
          {data.input.map((d, i) => (
            <div className="node-input" key={d}>
              <Handle
                id={d[0]}
                className="node-handle handle-input"
                type="target"
                position={Position.Left}
              />
              <Tag
                intent="danger"
                size="large"
                minimal
                round
                onRemove={removeIOVar("input")}
              >
                <EditText
                  idx={i}
                  style={{ padding: 0, minHeight: "10px" }}
                  defaultValue={d[0]}
                  // onChange={onEditIOVar}
                  onSave={onEditSaveIOVar("input", i)}
                />
              </Tag>
            </div>
          ))}
          <InputGroup
            className="node-input-output-add"
            round
            size="medium"
            placeholder="Add input..."
            rightElement={
              // <Tooltip content={`${showPassword ? "Hide" : "Show"} Password`} disabled={props.disabled}>
              <Button
                // disabled={props.disabled}
                icon={"plus"}
                // intent={Intent.WARNING}
                onClick={onAddIOVar("input")}
                variant="minimal"
              />
              // </Tooltip>
            }
            value={newInputVar}
            onValueChange={setNewInputVar}
          />
        </div>
        <div className="node-output-list">
          {data.output.map((d, i) => (
            <div className="node-output" key={d}>
              <Handle
                id={d}
                className="node-handle handle-output"
                type="source"
                position={Position.Right}
              />
              <Tag
                intent="primary"
                size="large"
                minimal
                round
                onRemove={removeIOVar("output")}
              >
                <EditText
                  idx={i}
                  style={{ padding: 0, minHeight: "10px" }}
                  defaultValue={d}
                  // onChange={onEditIOVar}
                  onSave={onEditSaveIOVar("output", i)}
                />
              </Tag>
            </div>
          ))}
          <InputGroup
            className="node-input-output-add"
            round
            size="medium"
            placeholder="Add output..."
            rightElement={
              // <Tooltip content={`${showPassword ? "Hide" : "Show"} Password`} disabled={props.disabled}>
              <Button
                // disabled={props.disabled}
                icon={"plus"}
                // intent={Intent.WARNING}
                onClick={onAddIOVar("output")}
                variant="minimal"
              />
              // </Tooltip>
            }
            value={newOutputVar}
            onValueChange={setNewOutputVar}
          />
        </div>
      </div>
      <Divider />
      <JsonView
        {...jsonViewConfig}
        className="output nodrag"
        src={data.exec}
        onEdit={updateNodeExec}
      />
    </BaseNode>
  );
}
