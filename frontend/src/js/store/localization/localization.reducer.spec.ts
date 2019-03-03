import { changeLanguage } from './localization.actions';
import localizationReducer, { initialState } from './localization.reducer';
import { LocalizationState } from './localization.types';

describe('Reducers::Localization reducer', () => {

  it('Should return the initial state', () => {
    const newState: any = {};
    const state: LocalizationState = localizationReducer(undefined, newState);
    expect(state).toEqual(initialState);
  });

  it('Should set auth info on login', () => {
    const state = localizationReducer(undefined, {
      type: changeLanguage.type,
      payload: {
        lang: 'be' ,
      },
    });
    expect(state.currentLanguage).toEqual('be');
  });

});
