import { createApp } from './app.js';

export default {
  fetch(request, env, executionContext) {
    return createApp(env).fetch(request, env, executionContext);
  },
};
