// SFS Zero-Spend Model Router for LangSmith Fleet.
// OpenAI-compatible chat/completions, OpenRouter Free -> Cloudflare Workers AI Free.
// Access is disabled until ROUTER_CLIENT_TOKEN is provisioned as a secret.
const ROUTER_MODEL = "sfs/free-router";
const CF_MODEL = "@cf/zai-org/glm-4.7-flash";
const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";
const MAX_BYTES = 192_000;
const MAX_TOKENS = 1024;
const send = (obj, code=200, headers={}) => Response.json(obj, {
  status:code,
  headers: {"Cache-Control":"no-store", ...headers}
});
const fail = (code, msg) => send({error:{message:msg,type:"sfs_router_error",code}},code);

async function equalSecret(a,b) {
  if (!a || !b) return false;
  const enc = new TextEncoder();
  const [x,y] = await Promise.all([crypto.subtle.digest("SHA-256",enc.encode(a)), crypto.subtle.digest("SHA-256",enc.encode(b))]);
  let diff = 0;
  const xa=new Uint8Array(x), ya=new Uint8Array(y);
  for (let i=0;i<xa.length;i++) diff|=xa[i]^ya[i];
  return diff===0;
}

function normalizeToolCalls(calls) {
  if (!Array.isArray(calls)) return undefined;
  return calls.map((x,i)=>{
    const f=x.function || x;
    const args=f.arguments ?? x.arguments ?? {};
    return {
      id: x.id || "call_sfs_"+i,
      type:"function",
      function:{
        name:f.name || x.name || "",
        arguments:typeof args==="string"?args:JSON.stringify(args)
      }
    };
  });
}

function normalizeCloudflare(result) {
  // Workers AI models expose different response envelopes. Handle the documented
  // text/tool-call shapes and reject unexpected output instead of fabricating success.
  if (result && Array.isArray(result.choices) && result.choices[0]?.message) {
    const choice=result.choices[0];
    const m=choice.message;
    const calls=normalizeToolCalls(m.tool_calls);
    const hasCalls=Array.isArray(calls) && calls.length>0;
    if (choice.finish_reason === "length") throw new Error("workers_ai_truncated_response");
    if ((typeof m.content!=="string" || !m.content.trim()) && !hasCalls) {
      throw new Error("workers_ai_empty_response");
    }
    return {role:"assistant",content:m.content ?? null, ...(hasCalls?{tool_calls:calls}:{})};
  }
  if (!result || (typeof result.response !== "string" &&
      typeof result.text !== "string" &&
      !Array.isArray(result.tool_calls))) throw new Error("workers_ai_invalid_response");
  const calls=normalizeToolCalls(result.tool_calls);
  const content=result.response ?? result.text ?? null;
  if ((!content || typeof content!=="string" || !content.trim()) && !calls?.length) {
    throw new Error("workers_ai_empty_response");
  }
  return {role:"assistant",content, ...(calls?.length?{tool_calls:calls}:{})};
}

function complete(message,model=ROUTER_MODEL) {
  return {
    id:"chatcmpl-sfs-"+crypto.randomUUID().replace(/-/g,""),
    object:"chat.completion",
    created:Math.floor(Date.now()/1000),
    model,
    choices:[{index:0,message,finish_reason:message.tool_calls?.length?"tool_calls":"stop"}]
  };
}

function asStream(obj) {
  // Delayed but standards-compatible SSE for Fleet clients requesting streaming.
  const c=obj.choices[0];
  const intro={id:obj.id,object:"chat.completion.chunk",created:obj.created,model:obj.model,
    choices:[{index:0,delta:{role:"assistant",...(c.message.content?{content:c.message.content}:{})},
      finish_reason:null}]};
  const events=["data: "+JSON.stringify(intro)+"\n\n"];
  if (c.message.tool_calls?.length) {
    events.push("data: "+JSON.stringify({
      id:obj.id,object:"chat.completion.chunk",created:obj.created,model:obj.model,
      choices:[{index:0,delta:{tool_calls:c.message.tool_calls.map((t,i)=>({index:i,...t}))},finish_reason:null}]
    })+"\n\n");
  }
  events.push("data: "+JSON.stringify({
    id:obj.id,object:"chat.completion.chunk",created:obj.created,model:obj.model,
    choices:[{index:0,delta:{},finish_reason:c.finish_reason}]
  })+"\n\n");
  events.push("data: [DONE]\n\n");
  return new Response(events.join(""), {headers:{
    "Content-Type":"text/event-stream; charset=utf-8",
    "Cache-Control":"no-store",
    "X-Accel-Buffering":"no"
  }});
}

async function primaryOpenRouter(body,env) {
  const payload={
    model:"openrouter/free",
    messages:body.messages,
    stream:false,
    max_tokens:Math.min(body.max_completion_tokens??body.max_tokens??MAX_TOKENS,MAX_TOKENS),
    ...(Array.isArray(body.tools)?{tools:body.tools}:{}),
    ...(body.tool_choice?{tool_choice:body.tool_choice}:{})
  };
  const r=await fetch(OPENROUTER_URL,{
    method:"POST",
    headers:{
      "authorization":"Bearer "+env.OPENROUTER_API_KEY,
      "content-type":"application/json",
      "x-title":"SFS CRM Integration Lab"
    },
    body:JSON.stringify(payload),
    signal:AbortSignal.timeout(18000)
  });
  if (r.status===400 || r.status===422) throw Object.assign(new Error("invalid_primary_request"),{clientFault:true});
  if (!r.ok) throw new Error("openrouter_unavailable_"+r.status);
  const data=await r.json();
  if (!data.choices?.[0]?.message) throw new Error("openrouter_missing_choice");
  const message=data.choices[0].message;
  if (data.choices[0].finish_reason==="length") throw new Error("openrouter_truncated_response");
  if ((typeof message.content!=="string" || !message.content.trim()) &&
      !message.tool_calls?.length) throw new Error("openrouter_invalid_result");
  return complete({role:"assistant",content:message.content??null,
      ...(message.tool_calls?.length?{tool_calls:normalizeToolCalls(message.tool_calls)}:{})});
}

async function secondaryWorkersAI(body,env) {
  if (!env.AI?.run) throw new Error("workers_ai_binding_missing");
  const tools=Array.isArray(body.tools)
    ?body.tools.filter(t=>t.type==="function" && t.function?.name)
      .map(t=>({name:t.function.name,description:t.function.description||"",parameters:t.function.parameters||{type:"object",properties:{}}}))
    :undefined;
  const data=await env.AI.run(CF_MODEL,{
    messages:body.messages,
    max_completion_tokens:Math.min(body.max_completion_tokens??body.max_tokens??MAX_TOKENS,MAX_TOKENS),
    chat_template_kwargs:{enable_thinking:false},
    ...(tools?.length?{tools}:{}),
    ...(body.tool_choice?{tool_choice:body.tool_choice}:{})
  });
  return complete(normalizeCloudflare(data));
}

export default {
  async fetch(req,env) {
    const url=new URL(req.url);
    if (url.pathname==="/health" && req.method==="GET") {
      return send({service:"sfs-zero-spend-router",ready:!!env.ROUTER_CLIENT_TOKEN,
        primary:!!env.OPENROUTER_API_KEY?"openrouter/free":"not_configured",
        secondary:CF_MODEL,zero_spend_mode:true});
    }
    if (!env.ROUTER_CLIENT_TOKEN) return fail(503,"Router credentials not configured");
    const bearer=req.headers.get("authorization")?.match(/^Bearer\s+(.+)$/i)?.[1]||"";
    if (!(await equalSecret(bearer,env.ROUTER_CLIENT_TOKEN))) return fail(401,"Unauthorized");
    if (url.pathname==="/v1/models" && req.method==="GET") {
      return send({object:"list",data:[{id:ROUTER_MODEL,object:"model",owned_by:"SFS"}]});
    }
    if (url.pathname!=="/v1/chat/completions" || req.method!=="POST") return fail(404,"Not found");
    const len=Number(req.headers.get("content-length")||0);
    if (len>MAX_BYTES) return fail(413,"Request too large");
    let raw;
    try {raw=await req.text();}catch {return fail(400,"Invalid request");}
    if (raw.length>MAX_BYTES) return fail(413,"Request too large");
    let body;
    try {body=JSON.parse(raw);}catch {return fail(400,"Invalid JSON");}
    if (!Array.isArray(body.messages)||body.messages.length===0||body.messages.length>40
      ||body.messages.some(m=>!["system","developer","user","assistant","tool"].includes(m?.role)))
      return fail(400,"messages must contain 1-40 supported roles");
    if (body.model!==ROUTER_MODEL && body.model!=="openai:sfs/free-router") return fail(400,"Only sfs/free-router is permitted");
    if (body.max_tokens!==undefined && (!Number.isInteger(body.max_tokens)||body.max_tokens<1))return fail(400,"Invalid max_tokens");
    if (body.max_completion_tokens!==undefined && (!Number.isInteger(body.max_completion_tokens)||body.max_completion_tokens<1))return fail(400,"Invalid max_completion_tokens");
    let out=null,route=null;
    if (env.OPENROUTER_API_KEY) {
      try {out=await primaryOpenRouter(body,env);route="openrouter/free";}
      catch(e) {if(e.clientFault)return fail(422,"Invalid request to free model");}
    }
    if (!out) {
      try {out=await secondaryWorkersAI(body,env);route=CF_MODEL;}
      catch {return fail(503,"All configured free model routes are unavailable or exhausted");}
    }
    const response=body.stream===true?asStream(out):send(out);
    response.headers.set("X-SFS-Route",route);
    response.headers.set("Cache-Control","no-store");
    return response;
  }
};
