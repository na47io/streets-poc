import { type Route, route, serveDir } from "@std/http";

const kv = await Deno.openKv();

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
  {
    pattern: new URLPattern({pathname: "/api/vote"}),
    method: "POST",
    handler: async (req) => {

      const {name, vote} = await req.json();

      // need to store each vote as an individual row in the database
      const key = vote == "hot" ? ["votes", "hot", name] : ["votes", "not", name]

      await kv
        .atomic()
        .mutate({
          type:"sum",
          key,
          value: new Deno.KvU64(1n)
        })
        .commit()

      return new Response("Vote cast", { status: 201 });
    }
  },
  {
    pattern: new URLPattern({pathname: "/api/vote"}),
    method: "GET",
    handler: async (req) => {
      const iter = kv.list<string>({prefix: ["votes"]});
      const votes = [];
      for await (const res of iter) votes.push(res);

      console.log(votes)
      return new Response(JSON.stringify(votes, (k,v) => 
        typeof v === "bigint" ? Number(v) : v
    ), { status: 200 });
    }
  }
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
