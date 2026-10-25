from pathlib import Path
import subprocess,json
from PIL import Image, ImageDraw, ImageFont
r=Path(__file__).resolve().parent;o=r/'rn-native';e=r/'explainer';e.mkdir(exist_ok=True);font='/System/Library/Fonts/Supplemental/Arial.ttf'
scenes=[
 ('intro',6,None,0,'A successful placement lookup can break a null guard\n\nReact Native Purchases / iOS\nPlacement configured as “No Offering”\nOctober 25, 2026 / upstream bde1095e'),
 ('before',7,'app-before.mp4',19,'BEFORE / real iOS app\n\nThe Test Store request succeeds.\nThe placement resolves undefined.\n\nA consumer checking offering !== null\ntries to read offering.identifier\nand throws TypeError.'),
 ('cause',9,None,0,'ROOT CAUSE\n\nThe iOS bridge resolves a nil offering.\nReact Native delivers that as undefined.\nThe TypeScript wrapper forwards it unchanged.\n\nIts public return type promises an offering or null.'),
 ('fix',8,None,0,'THE FIX\n\nAwait the native result and return offering ?? null.\nExisting offerings and rejected promises are preserved.\n\nNo public API signature change or consumer migration.\nNative error propagation is a separate fix: PR #2054.'),
 ('fixed',7,'app-fixed.mp4',7,'AFTER / same real iOS app\n\nSame source and dependency baseline.\nOnly null normalization changes.\n\nThe placement resolves null.\nThe same consumer shows “No offering”.'),
 ('verified',8,None,0,'CHECKED ON CURRENT SOURCE\n\nReal app: 1 failure + 1 pass → 2 passes\nFocused Jest regression: 1 failure + 4 passes → 5 passes\nAll 279 SDK tests, build and lint pass with the fix.\n\nSynthetic Test Store users. No purchases.\nAndroid app behavior was not tested.')]
for name,duration,source,start,caption in scenes:
 (e/(name+'.txt')).write_text(caption)
 bg=Image.new('RGB',(1920,1080),'#101523');draw=ImageDraw.Draw(bg);draw.multiline_text((70,210) if source else (110,210),caption,font=ImageFont.truetype(font,38 if source else 42),fill='white',spacing=24);bg.save(e/(name+'.png'))
 cmd=['ffmpeg','-y','-v','error','-loop','1','-framerate','30','-i',str(e/(name+'.png'))]
 if source:cmd+=['-ss',str(start),'-t',str(duration),'-i',str(o/source),'-filter_complex','[1:v]scale=-2:1000,setpts=PTS-STARTPTS[phone];[0:v][phone]overlay=1160:40:shortest=1,format=yuv420p[v]','-map','[v]']
 else:cmd+=['-vf','format=yuv420p']
 cmd+=['-t',str(duration),'-an','-c:v','libx264','-preset','fast','-crf','22','-movflags','+faststart',str(e/(name+'.mp4'))];subprocess.run(cmd,check=True)
(e/'concat.txt').write_text('\n'.join("file '"+n+".mp4'" for n,*_ in scenes));subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(e/'concat.txt'),'-c','copy','-movflags','+faststart',str(e/'placement-null-explainer.mp4')],check=True)
(e/'transcript.md').write_text('# Captioned explainer\n\nActual October 25 simulator footage and explanatory title cards. No voice narration.\n\n'+'\n\n'.join('## '+n+'\n\n'+c for n,d,s,t,c in scenes))
(e/'sources.json').write_text(json.dumps([dict(scene=n,seconds=d,source=s,start=t) for n,d,s,t,c in scenes],indent=2))
for stage,start in [('before',19),('fixed',7)]:subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(o/('app-'+stage+'.mp4')),'-t','7','-an','-c:v','libx264','-crf','20','-movflags','+faststart',str(o/(stage+'.mp4'))],check=True)
print('rendered')
