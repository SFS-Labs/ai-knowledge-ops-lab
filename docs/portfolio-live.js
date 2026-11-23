"use strict";
/* Public-only and opt-in GitHub metadata. Latest push != project evidence.
   Two independent browser actions: selected commit verification and a complete
   read-only public account inventory (GitHub owner type is User). */
const SOURCES = Object.freeze([
  {repo:"SFS-Labs/ctf-skills",label:"Cybersecurity / CTF Engineering"},
  {repo:"SFS-Labs/security-reviews",label:"REA / Security Reviews"},
  {repo:"SFS-Labs/ai-knowledge-ops-lab",label:"AI Knowledge Ops"}
]);
const PUBLIC_CLASS = Object.freeze({
  "SFS-Labs":"Profil / öffentliche Fallstudien",
  "ai-knowledge-ops-lab":"B2B AI / Integration",
  "tender-intelligence-case-study":"EU TED / Evaluation",
  "sfs-genomics":"Daten / OAuth MCP",
  "value-rail-mvp":"Monitoring / Validierung",
  "security-reviews":"Agenten / kontrolliertes MCP",
  "ctf-skills":"Cybersecurity / CTF",
  "ctf-skill-factory":"Historischer, archivierter Quellstand",
  "linkedin-preview-leadflow":"Review-Mockup, kein LinkedIn-Post",
  "agent-toolkit":"Atlan-Agent-Toolkit im SFS-Labs-Portfolio",
  "DamnVulnerableCryptoApp":"Security-Trainingsprojekt im SFS-Labs-Portfolio",
  "awesome-cryptocurrency-security":"Kuratierte Security-Quellen im SFS-Labs-Portfolio",
  "skills-introduction-to-github":"GitHub-Lernübung"
});
const button=document.getElementById("refresh-public-commits");
const list=document.getElementById("public-commit-list");
const status=document.getElementById("public-commit-status");
const allButton=document.getElementById("refresh-public-repositories");
const allList=document.getElementById("public-repository-list");
const allStatus=document.getElementById("public-repository-status");
function showStatus(element,message){if(element)element.textContent=message;}
async function getJSON(url){
  const response=await fetch(url,{mode:"cors",credentials:"omit",headers:{Accept:"application/vnd.github+json"}});
  if(!response.ok)throw new Error("GitHub "+response.status);
  return response.json();
}
function displayDate(s){const d=new Date(s);return Number.isNaN(d.valueOf())?"Datum unbekannt":d.toLocaleString("de-DE",{dateStyle:"medium",timeStyle:"short"});}
function addLinkItem(container,url,label,info){
  const li=document.createElement("li");
  const a=document.createElement("a");a.href=url;a.target="_blank";a.rel="noopener noreferrer";a.textContent=label;
  const span=document.createElement("span");span.textContent=info;
  li.append(a,span);container.appendChild(li);
}
if(button&&list&&status){
  button.addEventListener("click",async()=>{
    button.disabled=true;showStatus(status,"Öffentliche Commits werden direkt von GitHub abgefragt …");
    list.replaceChildren();
    try{
      const results=await Promise.allSettled(SOURCES.map(async ({repo,label})=>{
        const commits=await getJSON("https://api.github.com/repos/"+repo+"/commits?per_page=1");
        const c=commits?.[0];if(!c?.sha||!c?.commit)throw new Error("Empty repository");
        return{repo,label,sha:c.sha,date:c.commit.committer?.date||c.commit.author?.date};
      }));
      let successes=0;
      for(const res of results){
        if(res.status!=="fulfilled")continue;
        const x=res.value;successes++;
        addLinkItem(list,"https://github.com/"+x.repo+"/commit/"+encodeURIComponent(x.sha),
          x.label+" · "+x.sha.slice(0,8)," · "+displayDate(x.date));
      }
      showStatus(status,successes===SOURCES.length
        ?"Drei öffentliche Commit-Metadaten abgerufen. Ein neuer Commit beweist keine erfolgreiche CI oder Kundenwirkung."
        :successes+" von "+SOURCES.length+" Repo-Abfragen erfolgreich; übrige Daten aktuell nicht abrufbar.");
    }catch(_){
      showStatus(status,"GitHub-Metadaten nicht verfügbar; die datierten Fallstudien sind weiterhin lesbar.");
    }finally{button.disabled=false;}
  });
}
if(allButton&&allList&&allStatus){
  allButton.addEventListener("click",async()=>{
    allButton.disabled=true;allList.replaceChildren();
    showStatus(allStatus,"Öffentliche GitHub-Repositories werden abgefragt …");
    try{
      const repos=await getJSON("https://api.github.com/users/SFS-Labs/repos?per_page=100&sort=pushed");
      if(!Array.isArray(repos))throw new Error("Unexpected response");
      // Never display private or non-owned records, even in mocked/malformed responses.
      const safe=repos.filter(x=>x?.owner?.login==="SFS-Labs"&&x.private===false&&x.name&&
         /^[A-Za-z0-9_.-]+$/.test(x.name)&&x.html_url==="https://github.com/SFS-Labs/"+x.name);
      safe.sort((a,b)=>Date.parse(b.pushed_at||"")-Date.parse(a.pushed_at||""));
      for(const x of safe){
        const kind=PUBLIC_CLASS[x.name]||"Weiteres öffentliches SFS-Labs-Portfolio-Repository";
        const date=displayDate(x.pushed_at);
        addLinkItem(allList,x.html_url,x.name,
          " · "+kind+(x.archived?" · archiviert":"")+" · letzter Push: "+date);
      }
      showStatus(allStatus,safe.length+" öffentliche Repositories per GitHub-API gelesen"+
        (repos.length===100?" (maximal erste 100; Pagination noch nötig)":"")+
        ". Weitere Projektdetails und Tests finden Sie in den jeweiligen Repositories.");
    }catch(_){
      showStatus(allStatus,"Aktuelle öffentliche Repository-Liste nicht abrufbar (z. B. API-Ratenlimit). Keine Live-Vollständigkeit behauptet.");
    }finally{allButton.disabled=false;}
  });
}
