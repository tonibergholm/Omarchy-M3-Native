#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise pinned DCP colour selection; not a kernel/hardware test.

Requires a C compiler and ASan/UBSan. Reads supplied source trees and writes only
into a new output directory. Extracted DCP code retains GPL-2.0-only OR MIT and
Copyright 2021 Alyssa Rosenzweig. No firmware or hardware calls are made.
"""
from pathlib import Path
import argparse,hashlib,subprocess,json
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--reference-dir',type=Path,required=True,help='.20 apple driver source directory')
p.add_argument('--candidate-dir',type=Path,required=True,help='PR157 pinned apple driver source directory')
p.add_argument('--output',type=Path,required=True,help='new directory for generated tests/results')
a=p.parse_args()
def checked(path,expected):
 data=path.read_bytes()
 actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if actual!=expected:raise SystemExit(f'Unexpected source blob for {path}: {actual}')
 return data.decode()
up=checked(a.candidate_dir/'parser.c','bb8a49378fb005e055d688846a00bc6d44ba5f02')
ref=checked(a.reference_dir/'parser.c','2dfd85a19be3cf1c84d026a2f8a49578bc8c0cd4')
h=checked(a.candidate_dir/'parser.h','0557cc09e63e449213f2815806a163a7c0632aea')
r=a.output.resolve();r.mkdir(parents=True,exist_ok=False)

def unit(s,marker):
 start=s.index(marker);brace=s.index('{',start);level=1;i=brace+1
 while level:
  if s[i]=='{':level+=1
  elif s[i]=='}':level-=1
  i+=1
 return s[start:i]

def selection(s):
 start=s.index('\t\tif (cmode.eotf == DCP_EOTF_SDR_GAMMA)',s.index('static int parse_color_modes'))
 end=s.index('\n\t\tfill_color_mode(&out->best, &cmode);',start)+len('\n\t\tfill_color_mode(&out->best, &cmode);')
 return s[start:end]



enums=h[h.index('enum dcp_color_eotf'):h.index('/*',h.index('struct dcp_color_mode'))]
# C declarations only, ending immediately after the color-mode structure.
enums=enums[:enums.index('};',enums.index('struct dcp_color_mode'))+2]
preamble='''// SPDX-License-Identifier: GPL-2.0-only OR MIT
/* Extracted Apple DCP code: Copyright 2021 Alyssa Rosenzweig. */
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <errno.h>
#define U32_MAX UINT32_MAX
typedef int64_t s64; typedef uint32_t u32; typedef uint8_t u8;
'''+enums+'\nstruct dcp_display_mode { struct dcp_color_mode sdr_rgb,sdr_444,sdr,best; };\n'
old='''\t\t\t\tif (rank >= best_sdr_rank) {
\t\t\t\t\tif (rank > best_sdr_rank)
\t\t\t\t\t\tout->sdr_rgb.score = -1;
\t\t\t\t\tfill_color_mode(&out->sdr_rgb, &cmode);
\t\t\t\t\tbest_sdr_rank = rank;
\t\t\t\t}'''
new='''\t\t\t\tif (rank >= best_sdr_rank) {
\t\t\t\t\tstruct dcp_color_mode selected = out->sdr_rgb;

\t\t\t\t\tif (rank > best_sdr_rank)
\t\t\t\t\t\tselected.score = -1;
\t\t\t\t\tif (!fill_color_mode(&selected, &cmode)) {
\t\t\t\t\t\tout->sdr_rgb = selected;
\t\t\t\t\t\tbest_sdr_rank = rank;
\t\t\t\t\t}
\t\t\t\t}'''
assert up.count(old)==1
fixed=up.replace(old,new);(r/'upstream-parser-fixed.c').write_text(fixed)
priority=up[up.index('\tif (out->sdr_rgb.score >= 0)',up.index('static int parse_mode')):up.index('\n\n\ttrace_iomfb_parse_mode_success',up.index('static int parse_mode'))]
wrappers='static struct dcp_color_mode choose(struct color_mode *m,unsigned int n,bool p){return choose_all(m,n,p).sdr_rgb;}\nstatic int overall(struct color_mode *m,unsigned int n,bool p){struct dcp_display_mode all=choose_all(m,n,p),*out=&all; int best_color_mode=-1;\n'+priority+'\nreturn best_color_mode;}\n'
runner=r'''
static struct color_mode mode(int id,int color,int depth,int range,int score) {
 return (struct color_mode){.id=id,.colorimetry=color,.depth=depth,.dynamic_range=range,
 .eotf=DCP_EOTF_SDR_GAMMA,.pixel_encoding=DCP_COLOR_FORMAT_RGB,.score=score};
}
int main(void) {
 struct color_mode good=mode(69,DCP_COLORIMETRY_RGB,10,0,440999);
 int total=0,failed=0;
 for(int field=0;field<3;field++) for(int pos=0;pos<2;pos++) {
  struct color_mode bad=mode(99,DCP_COLORIMETRY_SRGB,8,0,500000);
  if(field==0)bad.depth=7; if(field==1)bad.depth=-1; if(field==2)bad.dynamic_range=-1;
  struct color_mode a[2]={pos?good:bad,pos?bad:good};
  struct dcp_color_mode got=choose(a,2,true);
  bool pass=got.id==69 && got.score==440999;
  printf("invalid_field=%d invalid_after_valid=%d id=%u score=%lld pass=%d\n",field,pos,got.id,(long long)got.score,pass);
  total++;failed+=!pass;
 }
 struct color_mode valid[3]={mode(68,DCP_COLORIMETRY_BT2020_RGB,10,0,447999),good,mode(70,DCP_COLORIMETRY_SRGB,8,0,100)};
 struct dcp_color_mode got=choose(valid,3,true); bool pass=got.id==70;total++;failed+=!pass;
 printf("valid_preference id=%u pass=%d\n",got.id,pass);
 got=choose(valid,3,false);pass=got.id==68;total++;failed+=!pass;
 printf("preference_disabled id=%u pass=%d\n",got.id,pass);
 struct color_mode bypass[3]={mode(71,DCP_COLORIMETRY_BT709,8,0,100),mode(68,DCP_COLORIMETRY_BT2020_RGB,10,0,447999),mode(99,DCP_COLORIMETRY_SRGB,7,0,500000)};
 int chosen=overall(bypass,3,true);pass=chosen==71;total++;failed+=!pass;
 printf("malformed_preferred_overall id=%d pass=%d\n",chosen,pass);
 printf("TOTAL=%d FAILED=%d\n",total,failed);return failed?1:0;
}
'''
results=[]
for name,s in [('reference',ref),('upstream',up),('fixed',fixed)]:
 parts=preamble+'\n'+unit(s,'struct color_mode {')+';\n'+unit(s,'static int fill_color_mode')+'\n'
 if name!='reference':parts+='static int external_colorimetry=DCP_COLORIMETRY_SRGB;\n'+unit(s,'static unsigned int external_colorimetry_rank')+'\n'
 parts+='static struct dcp_display_mode choose_all(struct color_mode *m,unsigned int n,bool prefer_colorimetry) {\nstruct dcp_display_mode result={0},*out=&result; out->sdr_rgb.score=out->sdr_444.score=out->sdr.score=out->best.score=-1; unsigned int best_sdr_rank=0; (void)best_sdr_rank;(void)prefer_colorimetry;\nfor(unsigned int i=0;i<n;i++){struct color_mode cmode=m[i];\n'+selection(s)+'\n}return result;}\n' + wrappers + runner
 if name=='reference':parts=parts.replace('pass=got.id==70','pass=got.id==68').replace('pass=chosen==71','pass=chosen==68')
 p=r/('selection-'+name+'.c');p.write_text(parts)
 build=subprocess.run(['cc','-Wall','-Wextra','-Wno-misleading-indentation','-fsanitize=address,undefined','-g',str(p),'-o',str(p.with_suffix(''))],capture_output=True,text=True,timeout=30)
 assert build.returncode==0,build.stderr
 run=subprocess.run([str(p.with_suffix(''))],capture_output=True,text=True,timeout=30)
 results.append({'variant':name,'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'compiler_stderr':build.stderr})
print(json.dumps(results,indent=2));(r/'selection-results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if [x['exit_code'] for x in results]==[0,1,0] else 1)
