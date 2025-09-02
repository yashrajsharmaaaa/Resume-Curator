import React, { createContext, useContext, useReducer } from 'react';

const AppContext = createContext();

const initialState = {
  resumes: [],
  currentResume: null,
  isUploading: false,
  error: null
};

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_UPLOADING':
      return { ...state, isUploading: action.payload, error: null };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isUploading: false };
    case 'ADD_RESUME':
      return { 
        ...state, 
        resumes: [...state.resumes, action.payload],
        currentResume: action.payload,
        isUploading: false,
        error: null
      };
    case 'SET_CURRENT_RESUME':
      return { ...state, currentResume: action.payload };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
}

export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const value = {
    ...state,
    dispatch
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};