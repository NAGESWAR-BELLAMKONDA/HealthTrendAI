import { useCallback, useEffect, useMemo, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import {
  Activity, AlertTriangle, ArrowDownRight, ArrowUpRight, BarChart3, BrainCircuit,
  CheckCircle2, Clock3, Database, Eye,
  FileBarChart2, Fingerprint, HeartPulse, Layers3, LineChart, LockKeyhole,
  LogOut, Mail, RefreshCw, Search, ShieldCheck, Sparkles, Users, Waves,
} from 'lucide-react';
import {
  Area, AreaChart, CartesianGrid, Legend, Line, LineChart as ReLineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import type { Session, User } from '@supabase/supabase-js';
import { isSupabaseConfigured, supabase } from './lib/supabase';

type Role = 'admin' | 'data_analyst' | 'researcher' | 'viewer';
type Page = 'Overview' | 'Disease Explorer' | 'Data Warehouse' | 'Data Mining' | 'ML Laboratory' | 'Forecasting' | 'Model Comparison' | 'Data Sources' | 'User Access';
type Row = Record<string, any>;
const ROLE_LABEL: Record<Role,string> = {admin:'Administrator',data_analyst:'Data Analyst',researcher:'Researcher',viewer:'Viewer'};
const PAGES: {name:Page;icon:ReactNode;roles:Role[]}[] = [
 {name:'Overview',icon:<BarChart3/>,roles:['admin','data_analyst','researcher','viewer']},
 {name:'Disease Explorer',icon:<Activity/>,roles:['admin','data_analyst','researcher','viewer']},
 {name:'Data Warehouse',icon:<Database/>,roles:['admin','data_analyst']},
 {name:'Data Mining',icon:<Layers3/>,roles:['admin','data_analyst','researcher']},
 {name:'ML Laboratory',icon:<BrainCircuit/>,roles:['admin','data_analyst']},
 {name:'Forecasting',icon:<Waves/>,roles:['admin','data_analyst','researcher']},
 {name:'Model Comparison',icon:<LineChart/>,roles:['admin','data_analyst','researcher']},
 {name:'Data Sources',icon:<FileBarChart2/>,roles:['admin','data_analyst','researcher','viewer']},
 {name:'User Access',icon:<Users/>,roles:['admin']},
];
const fmt=(v:unknown)=>Number(v??0).toLocaleString('en-IN',{maximumFractionDigits:1});
const dateFmt=(v:string)=>new Date(v+'T00:00:00').toLocaleDateString('en-IN',{month:'short',year:'2-digit'});
const roleAllowed=(role:Role,page:Page)=>PAGES.some(p=>p.name===page&&p.roles.includes(role));

export default function App(){
 const [session,setSession]=useState<Session|null>(null),[user,setUser]=useState<User|null>(null),[role,setRole]=useState<Role>('viewer');
 const [authMode,setAuthMode]=useState<'signin'|'signup'|'reset'>('signin'),[email,setEmail]=useState(''),[password,setPassword]=useState(''),[displayName,setDisplayName]=useState('');
 const [authBusy,setAuthBusy]=useState(false),[isRecovery,setIsRecovery]=useState(false),[authMessage,setAuthMessage]=useState(''),[authError,setAuthError]=useState('');
 const [page,setPage]=useState<Page>('Overview'),[loading,setLoading]=useState(false),[error,setError]=useState(''),[lastSync,setLastSync]=useState('');
 const [cases,setCases]=useState<Row[]>([]),[dates,setDates]=useState<Row[]>([]),[sources,setSources]=useState<Row[]>([]),[runs,setRuns]=useState<Row[]>([]),[forecasts,setForecasts]=useState<Row[]>([]),[mining,setMining]=useState<Row[]>([]),[admissions,setAdmissions]=useState<Row[]>([]),[roleRows,setRoleRows]=useState<Row[]>([]);
 const [query,setQuery]=useState(''),[diseaseFilter,setDiseaseFilter]=useState('All diseases');
 const [roleBusy,setRoleBusy]=useState('');
 const [realtime,setRealtime]=useState('connecting');

 const loadRole=useCallback(async (uid:string)=>{
   const {data,error}=await supabase.from('app_user_roles').select('role').eq('user_id',uid).maybeSingle();
   if(error){setRole('viewer');setError('Could not read your application role. Ask the administrator to verify the role table policy.');return;}
   const next=(data?.role??'viewer') as Role;setRole(next);
   setPage(p=>roleAllowed(next,p)?p:'Overview');
 },[]);
 const refresh=useCallback(async()=>{
   if(!session?.user)return;
   setLoading(true);setError('');
   const results=await Promise.all([
    supabase.from('fact_disease_cases').select('id,date_key,location_id,disease_id,source_id,case_count,measure_unit,is_estimated,dim_date!inner(full_date),dim_disease!inner(disease_name),dim_location!inner(location_label)').order('date_key',{ascending:true}).limit(2500),
    supabase.from('dataset_sources').select('id,source_name,publisher,source_url,geography,refresh_frequency,last_checked_at,last_loaded_at,is_active').order('created_at',{ascending:false}).limit(100),
    supabase.from('model_runs').select('id,target_name,model_name,model_family,mae,rmse,mape,status,test_start,test_end,created_at,metrics_details').order('created_at',{ascending:false}).limit(50),
    supabase.from('forecast_results').select('id,model_run_id,forecast_date,target_name,predicted_value,lower_bound,upper_bound,actual_value').order('forecast_date',{ascending:true}).limit(1500),
    supabase.from('mining_results').select('id,analysis_type,target_name,algorithm,status,result,sample_size,created_at,period_start,period_end').order('created_at',{ascending:false}).limit(50),
    supabase.from('fact_hospital_admissions').select('id,date_key,admission_count,measure_unit,source_note,dim_date!inner(full_date),dim_location!inner(location_label)').order('date_key',{ascending:true}).limit(2500),
   ]);
   const labels=['cases','sources','runs','forecasts','mining','admissions'];
   results.forEach((r,i)=>{if(r.error)setError(old=>old||labels[i]+': '+r.error!.message);});
   if(!results[0].error)setCases(results[0].data??[]);
   if(!results[1].error)setSources(results[1].data??[]);
   if(!results[2].error)setRuns(results[2].data??[]);
   if(!results[3].error)setForecasts(results[3].data??[]);
   if(!results[4].error)setMining(results[4].data??[]);
   if(!results[5].error)setAdmissions(results[5].data??[]);
   const d=await supabase.from('dim_date').select('date_key,full_date,year,month,month_name').order('date_key');
   if(!d.error)setDates(d.data??[]);
   setLastSync(new Date().toLocaleTimeString());
   setLoading(false);
 },[session]);

 useEffect(()=>{
   let alive=true;
   supabase.auth.getSession().then(({data})=>{if(!alive)return;setSession(data.session);setUser(data.session?.user??null);});
   const {data:{subscription}}=supabase.auth.onAuthStateChange((event,next)=>{setSession(next);setUser(next?.user??null);if(event==='PASSWORD_RECOVERY'){setAuthMode('reset');setIsRecovery(true);setEmail(next?.user?.email??'');setAuthMessage('Choose a new password for your account.');}});
   return()=>{alive=false;subscription.unsubscribe();};
 },[]);
 useEffect(()=>{if(session?.user)void loadRole(session.user.id);},[session?.user?.id,loadRole]);
 useEffect(()=>{if(session?.user)void refresh();else{setCases([]);setSources([]);setRuns([]);setForecasts([]);setMining([]);setAdmissions([]);}},[session?.user?.id,refresh]);
 useEffect(()=>{
   if(!session?.user)return;
   const channel=supabase.channel('healthtrend-live-warehouse')
    .on('postgres_changes',{event:'*',schema:'public',table:'fact_disease_cases'},()=>void refresh())
    .on('postgres_changes',{event:'*',schema:'public',table:'fact_hospital_admissions'},()=>void refresh())
    .on('postgres_changes',{event:'*',schema:'public',table:'model_runs'},()=>void refresh())
    .on('postgres_changes',{event:'*',schema:'public',table:'forecast_results'},()=>void refresh())
    .on('postgres_changes',{event:'*',schema:'public',table:'mining_results'},()=>void refresh())
    .subscribe(s=>setRealtime(s==='SUBSCRIBED'?'live':s.toLowerCase()));
   return()=>{void supabase.removeChannel(channel);};
 },[session?.user?.id,refresh]);

 const onAuth=async(e:FormEvent)=>{
  e.preventDefault();setAuthBusy(true);setAuthError('');setAuthMessage('');
  try{
   const redirectTo = authRedirectUrl();
   if(authMode==='signup'){
    const {data,error}=await supabase.auth.signUp({email:email.trim(),password,options:{data:{display_name:displayName.trim()},emailRedirectTo:redirectTo}});
    if(error)throw error;
    if(data.session){setAuthMessage('Account created. You are signed in.');}
    else setAuthMessage('Verification email sent. Open the message in your inbox, verify your address, then return here to sign in. Check Spam if needed.');
   }else if(authMode==='reset'){
    if(isRecovery){const {error}=await supabase.auth.updateUser({password});if(error)throw error;setIsRecovery(false);setAuthMessage('Password updated successfully.');}
    else{const {error}=await supabase.auth.resetPasswordForEmail(email.trim(),{redirectTo});if(error)throw error;setAuthMessage('Password reset instructions have been sent if this email belongs to an account.');}
   }else{
    const {error}=await supabase.auth.signInWithPassword({email:email.trim(),password});
    if(error)throw error;setAuthMessage('Signed in successfully.');
   }
  }catch(err){setAuthError(err instanceof Error?err.message:'Authentication failed.');}
  finally{setAuthBusy(false);}
 };
 const signOut=async()=>{await supabase.auth.signOut();setPage('Overview');setAuthMessage('');setIsRecovery(false);};
 const changeRole=async(uid:string,nextRole:Role)=>{
  setRoleBusy(uid);
  const {error}=await supabase.from('app_user_roles').update({role:nextRole}).eq('user_id',uid);
  if(error)setError(error.message);else await loadUsers();
  setRoleBusy('');
 };
 const loadUsers=async()=>{
  const [p,r]=await Promise.all([supabase.from('profiles').select('user_id,email,display_name,created_at').order('created_at',{ascending:false}),supabase.from('app_user_roles').select('user_id,role')]);
  if(p.error||r.error){setError(p.error?.message??r.error?.message??'Unable to load users');return;}
  const roles=new Map((r.data??[]).map((x:any)=>[x.user_id,x.role]));
  setRoleRows((p.data??[]).map((x:any)=>({...x,role:roles.get(x.user_id)??'viewer'})));
 };
 useEffect(()=>{if(role==='admin'&&page==='User Access')void loadUsers();},[role,page]);

 const monthly=useMemo(()=>{
  const grouped=new Map<string,number>();
  cases.forEach(r=>{const d=r.dim_date?.full_date;if(d){const k=d.slice(0,7);grouped.set(k,(grouped.get(k)??0)+Number(r.case_count));}});
  return [...grouped].sort(([a],[b])=>a.localeCompare(b)).map(([month,value])=>({month:dateFmt(month+'-01'),cases:value}));
 },[cases]);
 const diseaseNames=useMemo(()=>['All diseases',...new Set(cases.map(r=>r.dim_disease?.disease_name).filter(Boolean))], [cases]);
 const filteredCases=useMemo(()=>cases.filter(r=>(diseaseFilter==='All diseases'||r.dim_disease?.disease_name===diseaseFilter)&&(!query||JSON.stringify(r).toLowerCase().includes(query.toLowerCase()))),[cases,diseaseFilter,query]);
 const totalCases=cases.reduce((a,r)=>a+Number(r.case_count),0);
 const latest=monthly.at(-1),prior=monthly.at(-2);
 const delta=latest&&prior&&prior.cases?((latest.cases-prior.cases)/prior.cases)*100:null;
 const admissionsTotal=admissions.reduce((a,r)=>a+Number(r.admission_count),0);
 const pageRows=roleAllowed(role,page)?page:'Overview';

 if(!isSupabaseConfigured)return <div className="auth-shell"><div className="auth-card"><Brand/><h1>Connect your research workspace</h1><p>Configure the Supabase URL and publishable key to continue.</p></div></div>;
 if(!session||isRecovery)return <div className="auth-shell"><div className="auth-glow glow-one"/><div className="auth-glow glow-two"/><section className="auth-card"><Brand/><div className="auth-kicker"><Sparkles size={14}/> DATA MINING · HEALTH INTELLIGENCE</div><h1>{authMode==='signup'?'Create your research account':authMode==='reset'?'Reset your password':'Welcome back'}</h1><p className="auth-sub">A secure workspace for disease trend mining, data warehousing and evidence-based forecasting.</p>
  <div className="auth-tabs"><button className={authMode==='signin'?'selected':''} onClick={()=>{setAuthMode('signin');setAuthError('');setAuthMessage('');}}>Sign in</button><button className={authMode==='signup'?'selected':''} onClick={()=>{setAuthMode('signup');setAuthError('');setAuthMessage('');}}>Create account</button></div>
  <form onSubmit={onAuth} className="auth-form">
   {authMode==='signup'&&<label>Display name<input value={displayName} onChange={e=>setDisplayName(e.target.value)} placeholder="Your name" required autoComplete="name"/></label>}
   <label>Email address<div className="input-icon"><Mail size={16}/><input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="name@organization.com" required autoComplete="email"/></div></label>
   {authMode!=='reset'&&<label>Password<div className="input-icon"><LockKeyhole size={16}/><input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="At least 8 characters" minLength={8} required autoComplete={authMode==='signup'?'new-password':'current-password'}/></div></label>}
   {authMode==='signin'&&<button type="button" className="text-action" onClick={()=>{setAuthMode('reset');setAuthError('');setAuthMessage('');}}>Forgot password?</button>}
   <button className="primary-button" disabled={authBusy}>{authBusy?'Please wait…':authMode==='signup'?'Create secure account':authMode==='reset'?(isRecovery?'Update password':'Send reset link'):'Sign in to workspace'}<ArrowUpRight size={16}/></button>
  </form>
  {authError&&<div className="auth-alert error"><AlertTriangle size={16}/>{authError}</div>}
  {authMessage&&<div className="auth-alert success"><CheckCircle2 size={16}/>{authMessage}</div>}
  <div className="auth-foot"><ShieldCheck size={15}/> Email verification · Supabase Auth · Role-based permissions</div>
  <p className="role-note">New accounts start as Viewer. An administrator assigns Analyst, Researcher or Admin access.</p>
 </section><div className="auth-caption">HEALTHTREND AI <span>•</span> RESEARCH INTELLIGENCE PLATFORM</div></div>;

 return <div className="app-shell"><aside className="sidebar"><Brand/><div className="workspace-label">WORKSPACE</div><nav className="nav-list">{PAGES.filter(p=>p.roles.includes(role)).map(p=><button key={p.name} className={pageRows===p.name?'nav-item active':'nav-item'} onClick={()=>setPage(p.name)}>{p.icon}<span>{p.name}</span>{p.name==='Data Mining'&&mining.length>0&&<i className="nav-count">{mining.length}</i>}</button>)}</nav><div className="sidebar-bottom"><div className="security-card"><ShieldCheck size={17}/><div><b>Protected workspace</b><small>Row-level security active</small></div></div><div className="user-card"><div className="user-avatar">{(user?.email??'H').slice(0,1).toUpperCase()}</div><div className="user-meta"><b>{user?.user_metadata?.display_name||user?.email?.split('@')[0]}</b><small>{ROLE_LABEL[role]}</small></div><button title="Sign out" onClick={signOut}><LogOut size={16}/></button></div></div></aside>
 <main className="main-area"><header className="topbar"><div><div className="eyebrow">HEALTHTREND AI <span>/</span> {pageRows.toUpperCase()}</div><h1>{pageRows==='Overview'?'Disease intelligence overview':pageRows}</h1></div><div className="top-actions"><span className={'live-pill '+(realtime==='live'?'':'pending')}><i/>{realtime==='live'?'LIVE SYNC':realtime.toUpperCase()}</span><span className="sync-time"><Clock3 size={14}/>{lastSync?'Synced '+lastSync:'Sync pending'}</span><button className="icon-button" onClick={()=>void refresh()} disabled={loading} title="Refresh data"><RefreshCw size={16} className={loading?'spin':''}/></button><div className="top-avatar">{(user?.email??'H').slice(0,1).toUpperCase()}</div></div></header>
 {error&&<div className="inline-alert"><AlertTriangle size={16}/>{error}<button onClick={()=>setError('')}>Dismiss</button></div>}
 {pageRows==='Overview'&&<><section className="hero-banner"><div className="hero-orb"/><div className="hero-content"><div className="hero-tag"><Sparkles size={13}/> RESEARCH • DISCOVER • FORECAST</div><h2>Turn public health data<br/><em>into meaningful signals.</em></h2><p>Explore disease patterns, discover anomalies and compare forecasting methods using traceable public datasets.</p><div className="hero-meta"><span><Database size={14}/>{cases.length} verified observations</span><span><Fingerprint size={14}/>{ROLE_LABEL[role]} access</span></div></div><div className="hero-art"><div className="orbit orbit-a"/><div className="orbit orbit-b"/><div className="hero-center"><HeartPulse size={36}/></div><div className="orbit-dot dot-a"/><div className="orbit-dot dot-b"/><div className="orbit-dot dot-c"/></div></section>
 <section className="metric-grid"><Metric icon={<Activity/>} label="DISEASE OBSERVATIONS" value={fmt(cases.length)} foot="Rows in verified warehouse" tone="teal"/><Metric icon={<Database/>} label="AGGREGATE CASE COUNT" value={fmt(totalCases)} foot="Across loaded observations" tone="blue"/><Metric icon={<HeartPulse/>} label="HOSPITAL ADMISSIONS" value={admissions.length?fmt(admissionsTotal):'—'} foot={admissions.length?'HMIS validated records':'No validated HMIS data yet'} tone="violet"/><Metric icon={<BrainCircuit/>} label="COMPLETED MODEL RUNS" value={fmt(runs.filter(r=>r.status==='completed').length)} foot="Actual holdout evaluations" tone="amber"/></section>
 <section className="content-grid overview-grid"><Panel className="chart-panel"><SectionHead kicker="DISEASE TREND MINING" title="Monthly case observations" subtitle="Aggregated directly from Supabase warehouse" right={<span className="data-tag"><i/> DATABASE</span>}/>{monthly.length?<div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={monthly} margin={{top:12,right:10,left:-20,bottom:0}}><defs><linearGradient id="caseFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#4ce0c8" stopOpacity={.32}/><stop offset="100%" stopColor="#4ce0c8" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#23394b" strokeDasharray="4 6" vertical={false}/><XAxis dataKey="month" tick={{fill:'#8ca2b4',fontSize:10}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'#8ca2b4',fontSize:10}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'#101f30',border:'1px solid #29465a',borderRadius:12,color:'#e8f2f7'}}/><Area dataKey="cases" name="Cases" type="monotone" stroke="#4ce0c8" strokeWidth={2.5} fill="url(#caseFill)"/></AreaChart></ResponsiveContainer></div>:<Empty icon={<Database/>} title="No observations loaded" detail="Run a validated ETL pipeline to populate the warehouse."/>}<div className="chart-footer"><span>Monthly totals · all loaded diseases</span><span>{latest?latest.month+' latest':'Awaiting first load'}</span></div></Panel>
 <Panel><SectionHead kicker="SIGNAL SNAPSHOT" title="Latest movement" subtitle="Calculated from consecutive loaded periods"/><div className="signal-value">{latest?fmt(latest.cases):'—'}<small>cases · latest month</small></div><div className="signal-change">{delta===null?<span className="muted">Not enough periods to compare</span>:<><span className={delta>=0?'positive':'negative'}>{delta>=0?<ArrowUpRight size={16}/>:<ArrowDownRight size={16}/>} {Math.abs(delta).toFixed(1)}%</span><small>versus previous month</small></>}</div><div className="signal-divider"/><div className="mini-stat"><span>Active data sources</span><b>{sources.filter(s=>s.is_active).length}</b></div><div className="mini-stat"><span>Mining analyses saved</span><b>{mining.length}</b></div><div className="mini-stat"><span>Realtime channel</span><b className="status-text">{realtime==='live'?'Connected':'Connecting'}</b></div><button className="subtle-button" onClick={()=>setPage('Data Mining')}>Explore data mining <ArrowUpRight size={14}/></button></Panel></section>
 <section className="content-grid lower-grid"><Panel><SectionHead kicker="MODEL EVALUATION" title="Latest model results" subtitle="MAE · RMSE · MAPE from persisted test predictions" right={<button className="link-button" onClick={()=>setPage('Model Comparison')}>View all <ArrowUpRight size={14}/></button>}/>{runs.length?runs.slice(0,5).map(r=><ModelRow key={r.id} row={r}/>):<Empty icon={<BrainCircuit/>} title="No completed model runs" detail="Scores are withheld until a sufficient, continuous monthly series is available."/>}</Panel><Panel><SectionHead kicker="DATA PROVENANCE" title="Registered sources" subtitle="Publisher and source metadata"/>{sources.slice(0,4).map(s=><div className="source-row" key={s.id}><div className="source-icon"><Database size={15}/></div><div><b>{s.source_name}</b><small>{s.publisher}</small></div><a href={s.source_url} target="_blank" rel="noreferrer" aria-label="Open data source"><ArrowUpRight size={15}/></a></div>)}{!sources.length&&<Empty icon={<FileBarChart2/>} title="No source metadata" detail="Data source registry will appear here after ETL."/>}</Panel></section></>}
 {pageRows==='Disease Explorer'&&<><PageIntro title="Disease Explorer" text="Filter source-backed observations by disease and inspect monthly trends. Counts remain attached to their source, location and date dimensions."/><div className="filter-bar"><div className="search-field"><Search size={16}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search disease, source or location…"/></div><select value={diseaseFilter} onChange={e=>setDiseaseFilter(e.target.value)}>{diseaseNames.map(n=><option key={n}>{n}</option>)}</select><span className="result-count">{filteredCases.length} records</span></div><Panel><SectionHead kicker="OBSERVATION SERIES" title="Monthly observations" subtitle="No values are imputed or silently filled"/><div className="table-scroll"><table><thead><tr><th>MONTH</th><th>DISEASE</th><th>LOCATION</th><th>OBSERVATIONS</th><th>UNIT</th><th>QUALITY</th></tr></thead><tbody>{filteredCases.map(r=><tr key={r.id}><td>{r.dim_date?.full_date}</td><td>{r.dim_disease?.disease_name}</td><td>{r.dim_location?.location_label}</td><td>{fmt(r.case_count)}</td><td>{r.measure_unit}</td><td><span className="quality-pill">{r.is_estimated?'Estimated':'Source reported'}</span></td></tr>)}</tbody></table></div></Panel></>}
 {pageRows==='Data Warehouse'&&<><PageIntro title="Data Warehouse" text="Star-schema warehouse with source provenance, conformed dimensions and separate disease-case and hospital-admission fact tables."/><div className="warehouse-grid"><Metric icon={<Database/>} label="FACT: DISEASE CASES" value={fmt(cases.length)} foot="fact_disease_cases"/><Metric icon={<HeartPulse/>} label="FACT: ADMISSIONS" value={fmt(admissions.length)} foot="fact_hospital_admissions"/><Metric icon={<Clock3/>} label="DATE DIMENSION" value={fmt(dates.length)} foot="dim_date"/><Metric icon={<Layers3/>} label="DATA SOURCES" value={fmt(sources.length)} foot="dataset_sources"/></div><Panel><SectionHead kicker="DATA QUALITY & LINEAGE" title="Loaded warehouse records" subtitle="Latest source-backed observations"/><div className="table-scroll"><table><thead><tr><th>DATE</th><th>DISEASE</th><th>LOCATION</th><th>COUNT</th><th>SOURCE ID</th></tr></thead><tbody>{cases.slice(-50).reverse().map(r=><tr key={r.id}><td>{r.dim_date?.full_date}</td><td>{r.dim_disease?.disease_name}</td><td>{r.dim_location?.location_label}</td><td>{fmt(r.case_count)}</td><td className="mono">{String(r.source_id??'—').slice(0,12)}</td></tr>)}</tbody></table></div></Panel></>}
 {pageRows==='Data Mining'&&<><PageIntro title="Data Mining Studio" text="Descriptive trend analysis, period-over-period movement, anomaly screening, clustering and association discovery. Each analysis is saved with its algorithm and sample size."/><div className="analysis-grid"><AnalysisCard icon={<LineChart/>} title="Trend & growth analysis" desc="Monthly movement, rolling averages and linear trend direction." status={cases.length>=3?'Data available':'Needs more observations'}/><AnalysisCard icon={<Activity/>} title="Anomaly screening" desc="Robust median/MAD and z-score flags for unusual monthly values." status={cases.length>=8?'Data available':'Small sample'}/><AnalysisCard icon={<Layers3/>} title="Pattern grouping" desc="K-means grouping on normalized level, lag and calendar features." status={cases.length>=12?'Data available':'Small sample'}/><AnalysisCard icon={<BrainCircuit/>} title="Association & correlation" desc="Correlations between disease series and admissions only when aligned." status={cases.length?'Cases loaded':'Awaiting data'}/></div><Panel><SectionHead kicker="PERSISTED MINING OUTPUT" title="Analysis history" subtitle="Computed by the reproducible Python mining pipeline"/>{mining.length?mining.map(m=><div className="mining-row" key={m.id}><div className="analysis-icon"><Activity size={16}/></div><div className="mining-copy"><b>{m.analysis_type.replaceAll('_',' ')}</b><small>{m.algorithm} · {m.target_name.replaceAll('_',' ')} · n={m.sample_size}</small><small>{m.period_start??'—'} to {m.period_end??'—'}</small></div><span className={'status-chip '+m.status}>{m.status}</span><button className="icon-button" title="View analysis JSON" onClick={()=>window.alert(JSON.stringify(m.result,null,2))}><Eye size={15}/></button></div>):<Empty icon={<Layers3/>} title="No mining results yet" detail="The scheduled GitHub Actions mining pipeline will save verified analyses here when the input series meets each method's minimum sample requirement."/>}</Panel></>}
 {pageRows==='ML Laboratory'&&<><PageIntro title="Machine Learning Laboratory" text="Compare supervised regression methods on engineered lag, rolling-window and calendar features. Training uses chronological splits and prevents look-ahead leakage."/><div className="analysis-grid"><AnalysisCard icon={<BrainCircuit/>} title="Decision Tree Regressor" desc="Interpretable nonlinear baseline for lag features." status="Evaluation pipeline"/><AnalysisCard icon={<Layers3/>} title="Random Forest" desc="Ensemble of trees for nonlinear temporal features." status="Evaluation pipeline"/><AnalysisCard icon={<Sparkles/>} title="XGBoost" desc="Gradient-boosted trees; evaluated when installed in CI/runtime." status="Optional dependency"/></div><ModelTable runs={runs.filter(r=>r.model_family==='machine_learning')}/></>}
 {pageRows==='Forecasting'&&<><PageIntro title="Forecasting workspace" text="Inspect forecasts stored from rolling-origin model evaluation. Predictions are not clinical recommendations."/><Panel><SectionHead kicker="FORECAST OUTPUT" title="Predicted versus actual" subtitle="Only actual persisted forecast records are plotted"/>{forecasts.length?<div className="chart-wrap tall"><ResponsiveContainer width="100%" height="100%"><ReLineChart data={forecasts}><CartesianGrid stroke="#23394b" strokeDasharray="4 6"/><XAxis dataKey="forecast_date" tick={{fill:'#8ca2b4',fontSize:10}}/><YAxis tick={{fill:'#8ca2b4',fontSize:10}}/><Tooltip contentStyle={{background:'#101f30',border:'1px solid #29465a',borderRadius:12}}/><Legend/><Line type="monotone" dataKey="actual_value" name="Actual" stroke="#f2bd70" connectNulls dot={false}/><Line type="monotone" dataKey="predicted_value" name="Predicted" stroke="#4ce0c8" dot={false}/></ReLineChart></ResponsiveContainer></div>:<Empty icon={<Waves/>} title="No forecast points saved" detail="Forecast outputs appear after a model run completes successfully."/>}</Panel></>}
 {pageRows==='Model Comparison'&&<><PageIntro title="Model Comparison" text="Compare models using the same chronological holdout. MAE, RMSE and MAPE are computed from the same test observations."/><ModelTable runs={runs}/></>}
 {pageRows==='Data Sources'&&<><PageIntro title="Data Sources & Provenance" text="Open, public-health sources only. Refresh schedules follow the publisher's actual release cadence; this application does not invent live hospital feeds."/><div className="source-cards">{sources.map(s=><Panel key={s.id}><div className="source-card-head"><div className="source-icon"><Database size={17}/></div><span className={s.is_active?'quality-pill':'status-chip failed'}>{s.is_active?'Active':'Inactive'}</span></div><h3>{s.source_name}</h3><p>{s.publisher}</p><div className="source-meta"><span>Geography</span><b>{s.geography??'Not specified'}</b></div><div className="source-meta"><span>Refresh</span><b>{s.refresh_frequency??'Not specified'}</b></div><div className="source-meta"><span>Last loaded</span><b>{s.last_loaded_at?new Date(s.last_loaded_at).toLocaleString():'Not loaded'}</b></div><a className="source-link" href={s.source_url} target="_blank" rel="noreferrer">Open publisher source <ArrowUpRight size={14}/></a></Panel>)}</div>{!sources.length&&<Empty icon={<Database/>} title="No sources registered" detail="The ETL pipeline registers the exact source URL and report period when data is ingested."/>}</>}
 {pageRows==='User Access'&&<><PageIntro title="User access management" text="Assign least-privilege roles to verified accounts. New users are viewers until an administrator promotes them."/><Panel><SectionHead kicker="IDENTITY & ACCESS" title="Verified application accounts" subtitle="Roles are enforced in PostgreSQL row-level security"/><div className="table-scroll"><table><thead><tr><th>USER</th><th>EMAIL</th><th>CURRENT ROLE</th><th>ASSIGN ROLE</th><th>ACTION</th></tr></thead><tbody>{roleRows.map(r=><tr key={r.user_id}><td>{r.display_name||'—'}</td><td>{r.email}</td><td><span className="quality-pill">{ROLE_LABEL[r.role as Role]}</span></td><td><select value={r.role} onChange={e=>setRoleRows(old=>old.map(x=>x.user_id===r.user_id?{...x,role:e.target.value}:x))}><option value="viewer">Viewer</option><option value="researcher">Researcher</option><option value="data_analyst">Data Analyst</option><option value="admin">Administrator</option></select></td><td><button className="small-action" disabled={roleBusy===r.user_id||r.user_id===user?.id} onClick={()=>void changeRole(r.user_id,r.role as Role)}>{roleBusy===r.user_id?'Saving…':'Save role'}</button></td></tr>)}</tbody></table></div><p className="role-warning"><ShieldCheck size={15}/> Role changes are audited through the administrator workflow. Your own account cannot change its own role here.</p></Panel></>}
 <footer className="app-footer">HEALTHTREND AI <span>•</span> AGGREGATE RESEARCH INTELLIGENCE <span>•</span> NOT FOR CLINICAL DECISION-MAKING</footer></main></div>;
}

function Brand(){return <div className="brand"><div className="brand-mark"><HeartPulse size={21}/></div><div><b>HealthTrend <em>AI</em></b><small>HEALTH INTELLIGENCE</small></div></div>}
function Metric({icon,label,value,foot,tone}:{icon:ReactNode;label:string;value:string;foot:string;tone:string}){return <div className="metric-card"><div className={'metric-icon '+tone}>{icon}</div><small>{label}</small><strong>{value}</strong><p>{foot}</p></div>}
function Panel({children,className=''}:{children:ReactNode;className?:string}){return <section className={'panel '+className}>{children}</section>}
function SectionHead({kicker,title,subtitle,right}:{kicker:string;title:string;subtitle:string;right?:ReactNode}){return <div className="section-head"><div><small>{kicker}</small><h3>{title}</h3><p>{subtitle}</p></div>{right}</div>}
function Empty({icon,title,detail}:{icon:ReactNode;title:string;detail:string}){return <div className="empty-state"><div>{icon}</div><b>{title}</b><p>{detail}</p></div>}
function PageIntro({title,text}:{title:string;text:string}){return <div className="page-intro"><div><div className="eyebrow">ANALYTICS WORKSPACE</div><h2>{title}</h2><p>{text}</p></div><div className="intro-mark"><Sparkles size={24}/></div></div>}
function AnalysisCard({icon,title,desc,status}:{icon:ReactNode;title:string;desc:string;status:string}){return <div className="analysis-card"><div className="analysis-icon">{icon}</div><h3>{title}</h3><p>{desc}</p><small>{status}</small></div>}
function ModelRow({row}:{row:Row}){return <div className="model-row"><div className="model-symbol"><BrainCircuit size={16}/></div><div className="model-name"><b>{row.model_name}</b><small>{row.model_family==='machine_learning'?'Machine learning':'Time-series'} · {row.target_name?.replaceAll('_',' ')}</small></div><div className="model-metric"><small>MAE</small><b>{row.mae==null?'—':fmt(row.mae)}</b></div><div className="model-metric"><small>RMSE</small><b>{row.rmse==null?'—':fmt(row.rmse)}</b></div><div className="model-metric"><small>MAPE</small><b>{row.mape==null?'—':Number(row.mape).toFixed(2)+'%'}</b></div><span className={'status-chip '+row.status}>{row.status}</span></div>}
function ModelTable({runs}:{runs:Row[]}){return <Panel><SectionHead kicker="BENCHMARK RESULTS" title="Evaluation scorecard" subtitle="All scores use the same chronological test period"/>{runs.length?<div className="table-scroll"><table><thead><tr><th>MODEL</th><th>FAMILY</th><th>TEST PERIOD</th><th>MAE</th><th>RMSE</th><th>MAPE</th><th>STATUS</th></tr></thead><tbody>{runs.map(r=><tr key={r.id}><td><b>{r.model_name}</b></td><td>{r.model_family?.replaceAll('_',' ')}</td><td>{r.test_start} – {r.test_end}</td><td>{r.mae==null?'—':fmt(r.mae)}</td><td>{r.rmse==null?'—':fmt(r.rmse)}</td><td>{r.mape==null?'—':Number(r.mape).toFixed(2)+'%'}</td><td><span className={'status-chip '+r.status}>{r.status}</span></td></tr>)}</tbody></table></div>:<Empty icon={<BrainCircuit/>} title="No eligible benchmark results" detail="Models will be scored only after the series has sufficient continuous observations for a fair holdout comparison."/>}</Panel>}
