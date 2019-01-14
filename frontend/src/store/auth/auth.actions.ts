import typescriptFsa from 'typescript-fsa';
import { LoginActionPayload, UserAuth } from './auth.types';

const actionCreator = typescriptFsa();

export const login = actionCreator.async<LoginActionPayload, UserAuth>('LOGIN');
export const logout = actionCreator.async<{}, {}>('LOGOUT');
