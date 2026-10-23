from pathlib import Path
import subprocess,json,shutil
from PIL import Image, ImageDraw, ImageFont
r=Path(__file__).resolve().parent;o=r/'rn-native';e=r/'explainer';e.mkdir(exist_ok=True);font='/System/Library/Fonts/Supplemental/Arial.ttf'
scenes=[
 ('intro',5,None,0,'Placement failures disappear\nReact Native Purchases / iOS\n\nA real connection error resolves\nas undefined instead of rejecting.\n\nOctober 23, 2026 / upstream bde1095e'),
 ('before',10,'app-before.mp4',14,'BEFORE / live iOS app\n\nThe app points the SDK at a\nclosed local port.\n\ngetOfferings rejects with code 33.\nThe placement call resolves\nundefined and bypasses catch.'),
 ('cause',8,None,0,'ROOT CAUSE\n\nThe iOS placement completion receives\nboth an offering and an error.\n\nIt ignores the error and always calls resolve.\nThe SDK already has an error-aware helper.'),
 ('fix',8,None,0,'THE FIX\n\nRoute the completion through the existing\ngetResponseCompletionBlockWithResolve helper.\n\nNative errors now reject the JavaScript promise.\nPublic API signatures stay unchanged.'),
 ('fixed',9,'app-fixed.mp4',8,'AFTER / same live iOS app\n\nSame source baseline and dependencies.\nOnly the native bridge fix changes.\n\nThe placement request now rejects\nwith code 33. The app catches it.'),
 ('control',5,'app-fixed.mp4',22,'SUCCESS CONTROL\n\nThe real Test Store lookup still works.\nSynthetic user / no purchases.\n\nApp tests: 1 fail + 1 pass -> 2 pass\nNative tests: 1 fail + 3 pass -> 4 pass'),
]
for name,duration,source,start,caption in scenes:
 txt=e/(name+'.txt');txt.write_text(caption)
 bg=Image.new('RGB',(1920,1080),'#101523');draw=ImageDraw.Draw(bg)
 draw.multiline_text((75,200) if source else (120,250),caption,font=ImageFont.truetype(font,40 if source else 48),fill='white',spacing=22 if source else 24)
 bg.save(e/(name+'.png'))
 cmd=['ffmpeg','-y','-v','error','-loop','1','-framerate','30','-i',str(e/(name+'.png'))]
 if source:
  cmd+=['-ss',str(start),'-t',str(duration),'-i',str(o/source),'-filter_complex','[1:v]scale=-2:980,setpts=PTS-STARTPTS[phone];[0:v][phone]overlay=1180:50:shortest=1,format=yuv420p[v]','-map','[v]']
 else:cmd+=['-vf','format=yuv420p']
 cmd+=['-t',str(duration),'-an','-c:v','libx264','-preset','fast','-crf','22','-movflags','+faststart',str(e/(name+'.mp4'))]
 subprocess.run(cmd,check=True)
(e/'concat.txt').write_text('\n'.join("file '"+name+".mp4'" for name,*_ in scenes))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(e/'concat.txt'),'-c','copy','-movflags','+faststart',str(e/'placement-explainer.mp4')],check=True)
(e/'transcript.md').write_text('# Captioned explainer\n\nActual October 23 simulator footage interleaved with explanatory title cards. No voice narration.\n\n'+'\n\n'.join('## '+name+'\n\n'+caption for name,_,_,_,caption in scenes)+'\n')
(e/'sources.json').write_text(json.dumps([dict(scene=n,duration=d,source=s,start=t) for n,d,s,t,c in scenes],indent=2))
print('Rendered',e/'placement-explainer.mp4')
