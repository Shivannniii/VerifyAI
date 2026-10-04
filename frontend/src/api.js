const BASE_URL = import.meta.env?.VITE_API_URL ?? "";
const TOKEN_KEY="verifyai_token";
export const getToken=()=>localStorage.getItem(TOKEN_KEY); export const setToken=t=>localStorage.setItem(TOKEN_KEY,t); export const clearToken=()=>localStorage.removeItem(TOKEN_KEY);
export class ApiError extends Error{constructor(message,status){super(message);this.name="ApiError";this.status=status}}
let unauthorizedHandler=null; export const setUnauthorizedHandler=h=>{unauthorizedHandler=h};
function errorMessage(data,status){const d=data?.detail;if(typeof d==="string")return d;if(Array.isArray(d))return d.map(x=>x.msg||"").join(". ");return `Request failed (HTTP ${status})`}
async function request(path,{method="GET",json,formData,auth=true}={}){const headers={};const token=getToken();if(auth&&token)headers.Authorization=`Bearer ${token}`;let body;if(formData)body=formData;else if(json!==undefined){headers["Content-Type"]="application/json";body=JSON.stringify(json)}let res;try{res=await fetch(`${BASE_URL}/api${path}`,{method,headers,body})}catch{throw new ApiError("Cannot reach the server. Make sure the backend is running on port 8000.",0)}if(res.status===204)return null;let data=null;try{data=await res.json()}catch{}if(!res.ok){if(res.status===401&&auth&&token&&unauthorizedHandler)unauthorizedHandler();throw new ApiError(errorMessage(data,res.status),res.status)}return data}
export const api={
 register:(email,password)=>request("/auth/register",{method:"POST",json:{email,password},auth:false}),
 login:(email,password)=>request("/auth/login",{method:"POST",json:{email,password},auth:false}),
 me:()=>request("/auth/me"),
 listPapers:()=>request("/research"), uploadPdf:file=>{const f=new FormData();f.append("file",file);return request("/research/upload",{method:"POST",formData:f})},
 submitText:(text,title)=>request("/research/text",{method:"POST",json:{text,title:title||null}}), getPaper:id=>request(`/research/${id}`), getClaims:id=>request(`/research/${id}/claims`), analyze:id=>request(`/research/${id}/analyze`,{method:"POST"}), deletePaper:id=>request(`/research/${id}`,{method:"DELETE"}),
 verifyClaim:id=>request(`/verification/${id}/verify`,{method:"POST"}),
 detector:text=>request("/detector/analyze",{method:"POST",json:{text}}), detectorFile:file=>{const f=new FormData();f.append("file",file);return request("/detector/analyze-file",{method:"POST",formData:f})}, detectorHistory:()=>request("/detector/history"),
 dashboard:()=>request("/dashboard/stats"), report:id=>request(`/research/${id}/report`), reportMarkdown:id=>request(`/research/${id}/report/markdown`)
};
