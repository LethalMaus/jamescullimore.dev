#!/usr/bin/env node
// Original TestLens GitHub Actions collector. Never log the OIDC token.
import {createHash} from 'node:crypto';
import {readFile,realpath,rm,lstat} from 'node:fs/promises';
import {resolve,relative,dirname,isAbsolute} from 'node:path';
import {execFileSync,spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
export class CollectorError extends Error {}
const sha=text=>createHash('sha256').update(text.replace(/\r\n/g,'\n')).digest('hex');
const git=(root,...args)=>execFileSync('git',args,{cwd:root,encoding:'utf8',stdio:['ignore','pipe','pipe']}).trim();
export async function collect({root,connection,sources,report,command}){
 root=await realpath(root);
 if(!Array.isArray(command)||!command.length||!Array.isArray(sources)||!sources.length||sources.length>20)throw new CollectorError('Provide a test command and 1–20 tracked source paths.');
 const inside=path=>{const full=resolve(root,path),rel=relative(root,full);if(!rel||rel.startsWith('..')||isAbsolute(rel))throw new CollectorError('Paths must remain inside the checkout.');return full;};
 const trackedClean=()=>{
  if(git(root,'rev-parse','HEAD')!==connection.commit)throw new CollectorError('Checkout does not match approved commit.');
  if(git(root,'status','--porcelain','--untracked-files=no'))throw new CollectorError('Tracked checkout has modifications.');
 };
 async function snapshot(){return Promise.all(sources.map(async path=>{
  const full=inside(path);
  if(await realpath(full)!==full||(await lstat(full)).isSymbolicLink())throw new CollectorError('Source symlinks are unsupported.');
  git(root,'ls-files','--error-unmatch','--',path);
  const content=await readFile(full,'utf8');if(Buffer.byteLength(content)>120000)throw new CollectorError('Source is too large.');
  return {path,content,hash:sha(content)};
 }));}
 trackedClean();const before=await snapshot();
 const reportPath=inside(report);
 // Require an existing, real parent directory, preventing symlink escapes.
 if(await realpath(dirname(reportPath))!==dirname(reportPath))throw new CollectorError('Report directory must not use symlinks.');
 if(git(root,'ls-files','--',report))throw new CollectorError('The generated report must not be a tracked file.');
 await rm(reportPath,{force:true});
 const startedAt=new Date().toISOString();
 const run=spawnSync(command[0],command.slice(1),{cwd:root,stdio:'inherit',timeout:6*3600000});
 const finishedAt=new Date().toISOString();
 if(run.error||run.signal||run.status===null)throw new CollectorError('Test process did not finish. No evidence submitted.');
 trackedClean();const after=await snapshot();
 if(before.some((file,i)=>file.hash!==after[i].hash))throw new CollectorError('Source changed during the test run.');
 if((await lstat(reportPath)).isSymbolicLink()||await realpath(reportPath)!==reportPath)throw new CollectorError('Report symlinks are unsupported.');
 const junit=await readFile(reportPath,'utf8');if(Buffer.byteLength(junit)>120000)throw new CollectorError('Report is too large.');
 const packet={schemaVersion:1,connectionId:connection.id,workspace:connection.workspace,casesDigest:connection.casesDigest,revision:connection.commit,startedAt,finishedAt,exitCode:run.status,cleanBefore:true,cleanAfter:true,sources:before.map((file,i)=>({path:file.path,content:file.content,before:file.hash,after:after[i].hash})),junit};
 if(Buffer.byteLength(JSON.stringify(packet))>180000)throw new CollectorError('Evidence exceeds 180 KB limit.');
 return packet;
}
export async function submit(connection,packet){
 if(process.env.GITHUB_ACTIONS!=='true')throw new CollectorError('Submission requires GitHub Actions OIDC.');
 const target=new URL(connection.ingestUrl);
 if(target.protocol!=='https:'||!(target.hostname.endsWith('.atlassian-dev.net')||target.hostname.endsWith('.webtrigger.atlassian.app'))||target.username||target.password||target.hash)throw new CollectorError('Expected an Atlassian Forge ingestion URL.');
 if(connection.audience!==`${connection.ingestUrl}#${connection.id}`)throw new CollectorError('Connection audience mismatch.');
 const tokenEndpoint=new URL(process.env.ACTIONS_ID_TOKEN_REQUEST_URL??'');
 if(tokenEndpoint.protocol!=='https:'||!tokenEndpoint.hostname.endsWith('.actions.githubusercontent.com'))throw new CollectorError('Expected the GitHub Actions identity endpoint.');
 tokenEndpoint.searchParams.set('audience',connection.audience);
 const auth=process.env.ACTIONS_ID_TOKEN_REQUEST_TOKEN;if(!auth)throw new CollectorError('Workflow needs id-token: write permission.');
 const tokenResponse=await fetch(tokenEndpoint,{headers:{Authorization:`Bearer ${auth}`},redirect:'error',signal:AbortSignal.timeout(30000)});
 if(!tokenResponse.ok)throw new CollectorError(`GitHub identity request failed (${tokenResponse.status}).`);
 const {value:token}=await tokenResponse.json();if(typeof token!=='string'||token.length>16000)throw new CollectorError('Invalid GitHub identity response.');
 const response=await fetch(target,{method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify(packet),redirect:'error',signal:AbortSignal.timeout(30000)});
 if(!response.ok)throw new CollectorError(`TestLens rejected evidence (${response.status}). Check connection approval, source pins and workspace revision.`);
 console.log('TestLens accepted the authenticated workflow evidence. Check criterion results in Jira.');
}
async function main(){
 const [connectionPath,settingsPath]=process.argv.slice(2);if(!connectionPath||!settingsPath)throw new CollectorError('Usage: node testlens-ci.mjs connection.json testlens-run.json');
 const connection=JSON.parse(await readFile(connectionPath,'utf8')),settings=JSON.parse(await readFile(settingsPath,'utf8'));
 const packet=await collect({root:process.cwd(),connection,...settings});
 await submit(connection,packet);
 process.exitCode=packet.exitCode;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)main().catch(error=>{console.error(error instanceof CollectorError?error.message:'TestLens collection or submission failed. Verify the checkout and report settings. No credentials are printed.');process.exitCode=1;});
