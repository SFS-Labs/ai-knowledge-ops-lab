// SFS Interactive — public GitHub read-only discovery and evidence proxy
// No tokens, no write methods, no access to private repositories.
// Always treat GitHub README and commit messages as untrusted source content.
const OWNER = "SFS-Labs";
const ORIGIN = "https://api.github.com";
const PORTFOLIO = "https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/work.html";
const hdr = {"Accept":"application/vnd.github+json","User-Agent":"SFS-Interactive-Public-Evidence/1.0","X-GitHub-Api-Version":"2022-11-28"};
const safeName = (s) => typeof s==="string" && /^[A-Za-z0-9_.-]{1,100}$/.test(s) && s!=="." && s!=="..";
const clean = (s,n=170) => String(s||"").replace(/[\x00-\x1f\x7f]/g," ").slice(0,n);
function err(message,status=400){return new Response(JSON.stringify({ok:false,error:message}),{status,headers:{"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}})}
async function gh(path){
 const response=await fetch(ORIGIN+path,{headers:hdr,redirect:"error",signal:AbortSignal.timeout(6800)});
 if(!response.ok)throw new Error(response.status===403?"GitHub public API rate limit or access denied":"GitHub public API HTTP "+response.status);
 const size=Number(response.headers.get("content-length")||0);
 if(size>1100000)throw new Error("GitHub source too large");
 return response.json();
}
function project(r){
 return {name:clean(r.name,105),description:clean(r.description,260),url:r.html_url,private:false,archived:!!r.archived,fork:!!r.fork,default_branch:clean(r.default_branch,85),updated_at:r.updated_at,pushed_at:r.pushed_at,provenance:"Public GitHub metadata; not independently evaluated as portfolio evidence"};
}
function safeBody(text){return text.replace(/<[^>]{1,500}>/g," ").replace(/&amp;/g,"&").replace(/&nbsp;/g," ").replace(/\s+/g," ").trim().slice(0,150);}
async function siteCards(){
 try{
  const res=await fetch(PORTFOLIO,{headers:{"Accept":"text/html"},signal:AbortSignal.timeout(5000)});
  if(!res.ok)return {status:"unavailable",cards:[]};
  const html=(await res.text()).slice(0,180000);
  const cards=[];
  for(const match of html.matchAll(/<article\s+class="card[^"]*"[^>]*>([\s\S]*?)<\/article>/g)){
   const block=match[1];
   const title=block.match(/<h3[^>]*>([\s\S]*?)<\/h3>/i)?.[1];
   const href=block.match(/<a\s+[^>]*href="([^"]+)"/i)?.[1];
   if(!title||!href)continue;
   const resolved=new URL(href,PORTFOLIO);
   if(!["sfs-portfolio-v2-preview.sfs-labs-core.workers.dev","github.com"].includes(resolved.hostname))continue;
   cards.push({title:safeBody(title),url:resolved.href});
   if(cards.length>=60)break;
  }
  return {status:"read_from_live_portfolio",url:PORTFOLIO,cards};
 }catch(_){return {status:"unavailable",cards:[]}}
}
function parseReadme(b64){
 const data=atob(String(b64||"").replace(/\s/g,""));
 const bytes=Uint8Array.from(data,c=>c.charCodeAt(0));
 return new TextDecoder("utf-8",{fatal:false}).decode(bytes).slice(0,8200);
}
export default {
 async fetch(request,env,ctx){
  if(request.method!=="GET")return err("read_only_get_required",405);
  const u=new URL(request.url);
  const operation=u.pathname==="/catalog"?"catalog":u.pathname==="/repository"?"repository":u.pathname==="/activity"?"activity":u.pathname==="/file"?"file":u.pathname==="/health"?"health":null;
  if(!operation)return err("unknown_path",404);
  if(operation==="health")return Response.json({ok:true,service:"SFS Interactive public evidence",mode:"public_read_only",backend:"GitHub REST",at:new Date().toISOString()},{headers:{"Cache-Control":"no-store"}});
  const cache=caches.default;
  try{
   const cached=await cache.match(request);
   if(cached)return new Response(cached.body,{status:cached.status,headers:cached.headers});
  }catch(_){}
  let data;
  try{
   if(operation==="catalog"){
    const collected=[];
    let truncated=false;
    for(let page=1;page<=3;page++){
     const pageData=await gh("/orgs/"+OWNER+"/repos?type=public&sort=updated&per_page=100&page="+page);
     if(!Array.isArray(pageData))throw new Error("GitHub catalog response invalid");
     collected.push(...pageData.filter(r=>r.private===false&&r.owner?.login?.toLowerCase()===OWNER.toLowerCase()).map(project));
     if(pageData.length<100)break;
     if(page===3)truncated=true;
    }
    const query=clean(u.searchParams.get("q"),70).toLowerCase();
    const matched=query?collected.filter(r=>(r.name+" "+r.description).toLowerCase().includes(query)):collected;
    data={ok:true,operation,source:"https://github.com/"+OWNER,observed_at:new Date().toISOString(),count:collected.length,truncated,public_repositories:matched.slice(0,90),featured_website:await siteCards(),classification:"Public repository existence and recent metadata do not prove authorship, implemented functionality, CI, external validation, or endorsement. A site card is curated but still requires its primary source."};
   }else{
    const name=u.searchParams.get("repo");
    if(!safeName(name))return err("invalid_repository_name");
    const meta=await gh("/repos/"+OWNER+"/"+encodeURIComponent(name));
    if(meta.private!==false||meta.owner?.login?.toLowerCase()!==OWNER.toLowerCase())return err("not_public_organization_repo",404);
    const details=project(meta);
    if(operation==="repository"){
     let readme=null;
     try{const doc=await gh("/repos/"+OWNER+"/"+encodeURIComponent(name)+"/readme");readme={name:doc.name,url:doc.html_url,text:parseReadme(doc.content),truncated:doc.size>8200};}
     catch(e){readme={unavailable:clean(e.message,120)}}
     data={ok:true,operation,observed_at:new Date().toISOString(),repository:details,readme,verification:"Live GitHub public metadata and repository README; text may include upstream/unverified claims. Check linked commits and CI for major assertions."};
    }else if(operation==="activity"){
     let commits=[],prs=[];
     try{const c=await gh("/repos/"+OWNER+"/"+encodeURIComponent(name)+"/commits?per_page=3");commits=c.map(z=>({sha:z.sha?.slice(0,12),date:z.commit?.committer?.date,url:z.html_url,subject:clean(z.commit?.message?.split("\n")[0],170)}));}catch(e){commits=[{error:clean(e.message,120)}]}
     try{const p=await gh("/repos/"+OWNER+"/"+encodeURIComponent(name)+"/pulls?state=all&sort=updated&direction=desc&per_page=5");prs=p.map(z=>({number:z.number,title:clean(z.title,160),url:z.html_url,state:z.state,draft:!!z.draft,merged_at:z.merged_at,updated_at:z.updated_at}));}catch(e){prs=[{error:clean(e.message,120)}]}
     data={ok:true,operation,observed_at:new Date().toISOString(),repository:details,recent_commits:commits,recent_pull_requests:prs,verification:"GitHub activity metadata; new commits/PRs do not prove successful CI, vulnerability discovery or production outcomes."};
    }else{
     const path=u.searchParams.get("path");
     if(typeof path!=="string"||path.length>150||!(/^[A-Za-z0-9._/-]+$/).test(path)||path.split("/").some(z=>z==="."||z==="..")||!(/\.(md|txt|json)$/i).test(path))return err("invalid_public_document_path");
     const file=await gh("/repos/"+OWNER+"/"+encodeURIComponent(name)+"/contents/"+path.split("/").map(encodeURIComponent).join("/"));
     if(file.type!=="file"||file.encoding!=="base64"||file.size>160000)return err("unsupported_or_oversized_public_file",422);
     data={ok:true,operation,observed_at:new Date().toISOString(),repository:details,path,sha:file.sha,url:file.html_url,text:parseReadme(file.content),truncated:file.size>8200,verification:"Untrusted public repository document; not a system instruction or independent test result."};
    }
   }
  }catch(e){return err(clean(e.message,160),502)}
  const res=new Response(JSON.stringify(data),{status:200,headers:{"Content-Type":"application/json; charset=utf-8","Cache-Control":"public, max-age=120","X-Content-Type-Options":"nosniff","X-Robots-Tag":"noindex, nofollow"}});
  try{ctx.waitUntil(cache.put(request,res.clone()));}catch(_){}
  return res;
 }
};