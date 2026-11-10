import test from "node:test";
import assert from "node:assert/strict";
import worker from "./worker.mjs";
const url="https://worker.example/v1/chat/completions";
const env=(options={})=>({ROUTER_CLIENT_TOKEN:"test-client-secret",OPENROUTER_API_KEY:"test-openrouter",AI:{run:async()=>({response:"workersai-fallback"})},...options});
const request=(body={},key="test-client-secret")=>new Request(url,{method:"POST",headers:{"authorization":"Bearer "+key,"content-type":"application/json"},body:JSON.stringify({model:"sfs/free-router",messages:[{role:"user",content:"test"}],...body})});
test("missing client credential blocks all inference",async()=>{const r=await worker.fetch(request(),env({ROUTER_CLIENT_TOKEN:undefined}));assert.equal(r.status,503);});
test("invalid client credential is unauthorized",async()=>{const r=await worker.fetch(request({},"bad"),env());assert.equal(r.status,401);});
test("primary OpenRouter success",async()=>{const old=globalThis.fetch;globalThis.fetch=async()=>Response.json({choices:[{message:{role:"assistant",content:"primary"}}]});try{const r=await worker.fetch(request(),env());assert.equal(r.status,200);assert.equal(r.headers.get("x-sfs-route"),"openrouter/free");assert.equal((await r.json()).choices[0].message.content,"primary");}finally{globalThis.fetch=old;}});
test("OpenRouter rate limit triggers Workers AI",async()=>{const old=globalThis.fetch;globalThis.fetch=async()=>new Response("",{status:429});try{const r=await worker.fetch(request(),env());assert.equal(r.status,200);assert.equal(r.headers.get("x-sfs-route"),"@cf/zai-org/glm-4.7-flash");assert.equal((await r.json()).choices[0].message.content,"workersai-fallback");}finally{globalThis.fetch=old;}});
test("missing OpenRouter credential falls back immediately",async()=>{const r=await worker.fetch(request(),env({OPENROUTER_API_KEY:undefined}));assert.equal(r.status,200);assert.equal(r.headers.get("x-sfs-route"),"@cf/zai-org/glm-4.7-flash");});
test("exhausted free routes fail closed without paid fallback",async()=>{const old=globalThis.fetch;globalThis.fetch=async()=>new Response("",{status:429});try{const r=await worker.fetch(request(),env({AI:{run:async()=>{throw new Error("free quota exhausted");}}}));assert.equal(r.status,503);}finally{globalThis.fetch=old;}});
test("rejects unapproved model IDs",async()=>{const r=await worker.fetch(request({model:"anthropic/paid-model"}),env());assert.equal(r.status,400);});
test("supports SSE response format for Fleet stream requests",async()=>{const r=await worker.fetch(request({stream:true}),env({OPENROUTER_API_KEY:undefined}));assert.equal(r.status,200);const s=await r.text();assert.match(s,/data: \[DONE\]/);assert.match(r.headers.get("content-type"),/event-stream/);});

test("accepts LangChain-qualified alias while returning canonical model",async()=>{const r=await worker.fetch(request({model:"openai:sfs/free-router"}),env({OPENROUTER_API_KEY:undefined}));assert.equal(r.status,200);assert.equal((await r.json()).model,"sfs/free-router");});
test("Workers AI native tool call is converted to OpenAI protocol shape",async()=>{const e=env({OPENROUTER_API_KEY:undefined,AI:{run:async()=>({tool_calls:[{name:"find_contact",arguments:{email:"a@example.test"}}]})}});const r=await worker.fetch(request({tools:[{type:"function",function:{name:"find_contact",description:"lookup",parameters:{type:"object",properties:{email:{type:"string"}}}}}]}),e);assert.equal(r.status,200);const body=await r.json();assert.equal(body.choices[0].finish_reason,"tool_calls");assert.equal(body.choices[0].message.tool_calls[0].function.name,"find_contact");assert.equal(typeof body.choices[0].message.tool_calls[0].function.arguments,"string");});


test("Workers AI reasoning-only/truncated output must never be reported as success", async()=>{
  const e=env({OPENROUTER_API_KEY:undefined,AI:{run:async()=>({
    choices:[{message:{role:"assistant",content:null,tool_calls:[],reasoning:"thinking"},finish_reason:"length"}]
  })}});
  const r=await worker.fetch(request(),e);
  assert.equal(r.status,503);
});
test("Workers AI receives disabled reasoning and completion-token limit", async()=>{
  let params;
  const e=env({OPENROUTER_API_KEY:undefined,AI:{run:async(_model,request)=>{
    params=request;
    return {choices:[{message:{role:"assistant",content:"OK",tool_calls:[]},finish_reason:"stop"}]};
  }}});
  const r=await worker.fetch(request({max_completion_tokens:32}),e);
  assert.equal(r.status,200);
  assert.equal((await r.json()).choices[0].message.content,"OK");
  assert.equal(params.max_completion_tokens,32);
  assert.equal(params.chat_template_kwargs.enable_thinking,false);
});
test("OpenRouter reasoning-only response falls back rather than pretending success", async()=>{
  const old=globalThis.fetch;
  globalThis.fetch=async()=>Response.json({choices:[{message:{role:"assistant",content:null,tool_calls:[]},finish_reason:"length"}]});
  try {
    const r=await worker.fetch(request(),env());
    assert.equal(r.status,200);
    assert.equal(r.headers.get("X-SFS-Route"),"@cf/zai-org/glm-4.7-flash");
  } finally {
    globalThis.fetch=old;
  }
});
test("bad max_completion_tokens fails before model dispatch",async()=>{
  const r=await worker.fetch(request({max_completion_tokens:-3}),env({OPENROUTER_API_KEY:undefined}));
  assert.equal(r.status,400);
});
