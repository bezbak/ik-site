import { Container, getContainer } from "@cloudflare/containers";

// Single always-on instance: the site runs on SQLite, so requests must all
// land on the same container rather than being load-balanced across many.
export class DjangoContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "30m";

  constructor(ctx, env) {
    super(ctx, env);
    this.envVars = {
      ...this.envVars,
      DJANGO_DEBUG: "0",
      DJANGO_SECRET_KEY: env.DJANGO_SECRET_KEY,
      DJANGO_ALLOWED_HOSTS: env.DJANGO_ALLOWED_HOSTS,
    };
  }
}

export default {
  async fetch(request, env) {
    return getContainer(env.DJANGO_CONTAINER).fetch(request);
  },
};
