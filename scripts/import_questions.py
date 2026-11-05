import json,re,pathlib
root=pathlib.Path(__file__).resolve().parents[2]
def normalize(text):
 def table(m):
  rows=[r.strip().replace('$','') for r in m.group(1).split(r'\hline') if r.strip()]
  columns=max(r.count('&')+1 for r in rows)
  return '$'+r'\begin{array}{|'+'c|'*columns+'}'+r'\hline '+(' '+r'\\\hline'+' ').join(rows)+r'\\\hline\end{array}'+'$'
 return re.sub(r'\$\\begin\{tabular\}(.*?)\\end\{tabular\}\$',table,text,flags=re.S)
chapters=[]
for n in range(1,5):
 rows=json.loads((root/f'chap{n}.json').read_text())['list']
 chapters.append({'number':n,'title':rows[0]['chuong']['ten'],'questions':[{'id':str(r['cau_hoi']['id']),'text':normalize(r['cau_hoi']['noi_dung']),'type':r['cau_hoi']['loai'],'options':[{'id':o['id'],'text':normalize(o['content'])} for o in r['cau_hoi']['lua_chon']],'answers':r['cau_hoi']['dap_an']} for r in rows]})
(root/'on-tap-web/dist/data.js').write_text('window.CHAPTERS = '+json.dumps(chapters,ensure_ascii=False)+';')
