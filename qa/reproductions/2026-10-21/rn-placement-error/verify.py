import pathlib,subprocess,os,json,shutil
out=pathlib.Path(__file__).resolve().parent
b=out.parents[2];p=b/'publication/2026-10-20';app=b/'runs/2026-10-20/app';sdk=p/'rn-placement-error';installed=app/'node_modules/react-native-purchases'
base='c656a4274c6203c1c7d73c7a345307d2c1966a64';env=os.environ.copy();env.update(DEVELOPER_DIR='/Applications/Xcode-27.1.0-release.candidate.app/Contents/Developer',FORCE_BUNDLING='1',CI='true',LANG='en_US.UTF-8',LC_ALL='en_US.UTF-8')
results=[]
def run(name,args,cwd,expected=0):
 print(name,flush=True)
 with (out/(name+'.log')).open('w') as f:r=subprocess.run(args,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':args,'exit':r.returncode,'expected':expected});(out/'commands.json').write_text(json.dumps(results,indent=2))
 if r.returncode!=expected:raise RuntimeError(name+': '+str(r.returncode))
run('sdk-build',['corepack','yarn','build'],sdk)
run('regression-before',['python3','scripts/placement_error_contract.py',base,'before'],sdk,1)
run('regression-fixed',['python3','scripts/placement_error_contract.py'],sdk)
run('core-tests',['corepack','yarn','test','--runInBand'],sdk)
run('typecheck',['corepack','yarn','typecheck'],sdk)
# Use current upstream JS and the same dependency lock for both app runs. Only RNPurchases.m differs.
original={f:(installed/f).read_bytes() for f in ['ios/RNPurchases.m','dist/purchases.js']}
for f,v in original.items():
 dest=out/'original-installed'/f;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(v)
shutil.copy2(p/'current-apps/rn-placement/sdk/dist/purchases.js',installed/'dist/purchases.js')
shutil.copy2(app/'ios/Podfile.lock',out/'Podfile.lock')
sim='286DC73D-2455-4F1B-A4A2-56E3BDEE64D9'
run('boot',['xcrun','simctl','bootstatus',sim,'-b'],app)
cmd=['xcodebuild','-workspace','ios/RCBugReporter.xcworkspace','-scheme','QAReproduction','-configuration','Debug','-destination','platform=iOS Simulator,id='+sim,'-derivedDataPath',str(b/'runs/2026-10-20/derived-app'),'CODE_SIGNING_ALLOWED=NO']
try:
 for stage,expected in [('before',65),('fixed',0)]:
  data=subprocess.check_output(['git','show',base+':ios/RNPurchases.m'],cwd=sdk) if stage=='before' else (sdk/'ios/RNPurchases.m').read_bytes()
  (installed/'ios/RNPurchases.m').write_bytes(data)
  run('app-build-'+stage,cmd+['build-for-testing'],app)
  run('app-tests-'+stage,cmd+['test-without-building','-parallel-testing-enabled','NO','-only-testing:RCBugReporterUITests/ReproductionTests/testNetworkError','-only-testing:RCBugReporterUITests/ReproductionTests/testOnlineControl','-resultBundlePath',str(out/(stage+'.xcresult'))],app,expected)
  run('attachments-'+stage,['xcrun','xcresulttool','export','attachments','--path',str(out/(stage+'.xcresult')),'--output-path',str(out/('attachments-'+stage))],app)
finally:
 for f,v in original.items():(installed/f).write_bytes(v)
(out/'verification.json').write_text(json.dumps({'upstream':base,'fix':subprocess.check_output(['git','rev-parse','HEAD'],cwd=sdk,text=True).strip(),'onlyFix':'ios placement error propagation','commands':results},indent=2))
