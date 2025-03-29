// load comm type classes from json
const loadConstantsFromJson = async (url) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  const data = await response.json();
  const constants = {};
  for (const [key, value] of Object.entries(data)) {
    constants[key] = value;
  }
  return constants;
};
const constants = await loadConstantsFromJson("constants.json");

export const { MsgType, InteractionType, Status } = constants;
