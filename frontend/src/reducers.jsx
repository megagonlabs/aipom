export const initialChatState = {
  messages: [],
  nextId: 0, // Keeps track of the next message ID
};

export const chatReducer = (state, action) => {
  switch (action.type) {
    case "ADD_USER_MESSAGE":
      return {
        ...state,
        messages: [
          ...state.messages,
          // { id: state.nextId, role: "user", content: action.payload, timestamp: Date.now() },
          { ...action.payload, id: state.nextId },
        ],
        nextId: state.nextId + 1,
      };
    case "ADD_SYSTEM_RESPONSE":
      return {
        ...state,
        messages: [...state.messages, { ...action.payload, id: state.nextId }],
        nextId: state.nextId + 1,
      };
    case "CLEAR_CHAT":
      return { ...initialChatState };
    case "SET_CHAT_HISTORY": {
      const nextId = action.payload.length ? action.payload.at(-1).id + 1 : 0;
      return { messages: action.payload, nextId };
    }
    default:
      return state;
  }
};
