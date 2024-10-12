import { type Route, route, serveDir } from "@std/http";

const routes: Route[] = [
  {
    pattern: new URLPattern({ pathname: "/" }),
    handler: () => {
      // return html from static/index.html
      //
      //
      const html = Deno.readTextFileSync("./static/index.html");

      const resp = new Response(html,{
        status:200,
        headers: {
          "content-type": "text/html",
        },
      })

      return resp;
    }
  },
  {
    pattern: new URLPattern({ pathname: "/users/:id" }),
    handler: (_req, _info, params) => new Response(params?.pathname.groups.id),
  },
  {
    pattern: new URLPattern({ pathname: "/static/*" }),
    handler: (req) => serveDir(req),
  },
];

function defaultHandler(_req: Request) {
  return new Response("Not found", { status: 404 });
}

const handler = route(routes, defaultHandler);

export default {
  fetch(req) {
    return handler(req);
  },
} satisfies Deno.ServeDefaultExport;
