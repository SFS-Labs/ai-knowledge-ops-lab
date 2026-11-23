"use strict";
/* Read-only opt-in GitHub metadata. This is NOT a statement about the latest
   security validation, quality, customer deployment, or test outcomes. */
const SOURCES = Object.freeze([
 {repo:"SFS-Labs/ctf-skills",label:"CTF / Freebuff"},
 {repo:"SFS-Labs/security-reviews",label:"REA / Security Reviews"},
 {repo:"SFS-Labs/ai-knowledge-ops-lab",label:"AI Knowledge Ops"}
]);
const button=document.getElementById("refresh-public-commits");
const list=document.getElementById("public-commit-list");
const status=document.getElementById("public-commit-status");
function showStatus(message){if(status)status.textContent=message;}
if(button&&list&&status){
 button.addEventListener("click",async()=>{
  button.disabled=true;showStatus("Öffentliche GitHub-Commits werden abgerufen …");
  list.replaceChildren();
  try{
   const output=await Promise.all(SOURCES.map(async ({repo,label})=>{
    const response=await fetch("https://api.github.com/repos/"+repo+"/commits?per_page=1",{
       mode:"cors",credentials:"omit",headers:{"Accept":"application/vnd.github+json"}
    });
    if(!response.ok)throw new Error("GitHub "+response.status);
    const commits=await response.json();
    const item=commits&&commits[0];
    if(!item||!item.sha||!item.commit)throw new Error("Keine GitHub-Antwort");
    const date=new Date(item.commit.committer?.date||item.commit.author?.date);
    return {label,sha:item.sha.slice(0,8),url:"https://github.com/"+repo+"/commit/"+encodeURIComponent(item.sha),date:Number.isNaN(date.valueOf())?"Datum unbekannt":date.toLocaleString("de-DE",{dateStyle:"medium",timeStyle:"short"})};
   }));
   for(const x of output){
     const row=document.createElement("li");
     const a=document.createElement("a");
     a.href=x.url;a.target="_blank";a.rel="noopener noreferrer";
     a.textContent=x.label+" · "+x.sha;
     const span=document.createElement("span");
     span.textContent=" · "+x.date;
     row.append(a,span);list.appendChild(row);
   }
   showStatus("Öffentliche Repository-Metadaten direkt von GitHub. Ein neuer Commit bestätigt keine ausgeführten Tests oder neue Agentenfähigkeiten.");
  }catch(e){
   showStatus("Der Live-Abruf ist nicht verfügbar (z. B. GitHub-Rate-Limit). Projektlinks und datierte Fallstudien bleiben nutzbar.");
  }finally{button.disabled=false;}
 });
}
