import { combineReducers, AnyAction } from 'redux'
import {
  GET_SIZES_REQUEST,
  GET_SIZES_SUCCESS,
  GET_SIZES_FAILURE,
  GET_WORKSPACES_REQUEST,
  GET_WORKSPACES_SUCCESS,
  GET_WORKSPACES_FAILURE,
  START_SERVER_REQUEST,
  START_SERVER_SUCCESS,
  START_SERVER_FAILURE,
  STOP_SERVER_REQUEST,
  STOP_SERVER_SUCCESS,
  STOP_SERVER_FAILURE
} from './actions'
import add, { AddWorkspaceStoreState } from './AddWorkspace/reducer';



interface GetWorkspacesStoreState {
  serverSizes: any,
  workspaces: any,
  serverRunning: boolean
}

const initialState = {
  serverSizes: [],
  workspaces: [],
  serverRunning: false
}

const servers = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case GET_SIZES_REQUEST:
      return {
        ...state
      }
    case GET_SIZES_SUCCESS:
      return {
        ...state,
        serverSizes: action.data
      }
    case GET_SIZES_FAILURE:
      return {
        ...state
      }
    case GET_WORKSPACES_REQUEST:
      return {
        ...state
      }
    case GET_WORKSPACES_SUCCESS:
    console.log('get ws success', action.data)
      return {
        ...state,
        workspaces: action.data
      }
    case GET_WORKSPACES_FAILURE:
      return {
        ...state
      }
    case START_SERVER_REQUEST:
      return {
        ...state,
        serverRunning: false
      }
    case START_SERVER_SUCCESS:
      return {
        ...state,
        serverRunning: true
      }
    case START_SERVER_FAILURE:
      return {
        ...state
      }
    case STOP_SERVER_REQUEST:
      return {
        ...state,
        serverRunning: true
      }
    case STOP_SERVER_SUCCESS:
      return {
        ...state,
        serverRunning: false
      }
    case STOP_SERVER_FAILURE:
      return {
        ...state
      }
    default:
      return state
  }
}

export interface WorkspacesStoreState {
  servers: GetWorkspacesStoreState,
  add: AddWorkspaceStoreState
}

const workspaces = combineReducers({
  servers,
  add
})

export default workspaces