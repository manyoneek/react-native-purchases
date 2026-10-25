from pathlib import Path
import urllib.request,subprocess,json,hashlib
r=Path(__file__).resolve().parent;w=r/'worktrees/purchases-android';d=r/'android-queue';d.mkdir(exist_ok=True);cache=Path.home()/'.gradle/caches/modules-2/files-2.1';java='/opt/homebrew/opt/openjdk@21/bin/java'
def jar(pattern):return str(next(cache.glob(pattern)))
jars=[]
for name,url in [('junit-4.13.2.jar','junit/junit/4.13.2/junit-4.13.2.jar'),('hamcrest-core-1.3.jar','org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar'),('assertj-core-3.22.0.jar','org/assertj/assertj-core/3.22.0/assertj-core-3.22.0.jar')]:
 p=d/name;urllib.request.urlretrieve('https://repo.maven.apache.org/maven2/'+url,p);jars.append(str(p))
std=jar('org.jetbrains.kotlin/kotlin-stdlib/2.0.21/*/*.jar');annotations=jar('org.jetbrains/annotations/13.0/*/*.jar');cp=':'.join(jars+[std,annotations])
compiler=':'.join([jar('org.jetbrains.kotlin/kotlin-compiler-embeddable/2.0.21/*/*.jar'),std,jar('org.jetbrains.kotlin/kotlin-script-runtime/2.0.21/*/*.jar'),jar('org.jetbrains.kotlin/kotlin-reflect/2.0.21/*/*.jar'),jar('org.jetbrains.intellij.deps/trove4j/*/*/*.jar'),jar('org.jetbrains.kotlinx/kotlinx-coroutines-core-jvm/1.6.4/*/*.jar'),annotations])
sources=[w/'purchases/src/main/kotlin/com/revenuecat/purchases/virtualcurrencies/PerUserSerialQueue.kt',w/'purchases/src/test/java/com/revenuecat/purchases/virtualcurrencies/PerUserSerialQueueTest.kt']
records=[]
def run(name,args):
 p=subprocess.run(args,capture_output=True,text=True);(d/(name+'.log')).write_text(p.stdout+p.stderr);records.append({'name':name,'command':args,'exit':p.returncode});(d/'extended-commands.json').write_text(json.dumps(records,indent=2));print(name,p.returncode,p.stdout[-1000:],p.stderr[-1000:]);p.check_returncode()
sources.append(d/'PerUserSerialQueueContractTest.kt')
run('compile-extended',[java,'-cp',compiler,'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-language-version','1.8','-jvm-target','1.8','-classpath',cp,'-d',str(d/'classes'),*map(str,sources)])
run('extended',[java,'-cp',str(d/'classes')+':'+cp,'org.junit.runner.JUnitCore','com.revenuecat.purchases.virtualcurrencies.PerUserSerialQueueTest','com.revenuecat.purchases.virtualcurrencies.PerUserSerialQueueContractTest'])
(d/'dependencies.json').write_text(json.dumps([{'file':p,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in (cp+':'+compiler).split(':')],indent=2))
