import re, math

def analyze_text(text):
    text=(text or "").strip(); words=re.findall(r"\b[\w'-]+\b",text.lower()); sentences=[s for s in re.split(r"(?<=[.!?])\s+",text) if s.strip()]
    n=len(words); sn=len(sentences)
    if n<20: return {"word_count":n,"sentence_count":sn,"ai_probability":0.5,"human_probability":0.5,"confidence":0.1,"classification":"uncertain","mode":"baseline","explanation":"Provide at least a few full sentences for a meaningful screening result."}
    unique=len(set(words)); diversity=unique/max(1,n); repeats=1-diversity
    lengths=[len(re.findall(r"\b\w+\b",s)) for s in sentences]; mean=sum(lengths)/len(lengths); variance=sum((x-mean)**2 for x in lengths)/len(lengths); variation=min(1,math.sqrt(variance)/max(1,mean))
    formula=sum(1 for p in ["in conclusion","it is important to note","furthermore","moreover","in today's world","this highlights","plays a crucial role","overall"] if p in text.lower())
    repetitive=1 if re.search(r"\b(\w+)\s+\1\b",text.lower()) else 0
    numeric=len(re.findall(r"\b\d+(?:\.\d+)?%?\b",text))/max(1,n)
    ai=max(0,min(1,0.48 + repeats*.75 - variation*.35 + min(formula,.3) + repetitive*.08 - min(numeric,.08)))
    human=1-ai; conf=min(.92,abs(ai-.5)*1.8+.2)
    if ai>=.62: cls="likely_ai"
    elif ai<=.38: cls="likely_human"
    else: cls="uncertain"
    return {"word_count":n,"sentence_count":sn,"ai_probability":round(ai,3),"human_probability":round(human,3),"confidence":round(conf,3),"classification":cls,"mode":"baseline","explanation":"This is a lightweight screening heuristic based on lexical diversity, repetition, sentence-length variation and formulaic phrasing. It is not proof of authorship."}
