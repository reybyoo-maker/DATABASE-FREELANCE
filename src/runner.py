import argparse, hashlib, json, logging, os, re, sys, time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
L = logging.getLogger("database-freelance")
TZ = ZoneInfo("Asia/Jakarta")
UA = "DATABASE-FREELANCE/1.0 public business research"
SOCIAL = {"instagram.com":"instagram","facebook.com":"facebook","fb.com":"facebook","linkedin.com":"linkedin","tiktok.com":"tiktok","x.com":"other_social","twitter.com":"other_social","youtube.com":"other_social","threads.net":"other_social"}
REGIONS = [
("Jakarta","Indonesia"),("Bandung","Indonesia"),("Surabaya","Indonesia"),("Yogyakarta","Indonesia"),("Medan","Indonesia"),("Makassar","Indonesia"),("Bali","Indonesia"),
("Kuala Lumpur","Malaysia"),("Singapore","Singapore"),("Bangkok","Thailand"),("Manila","Philippines"),("Hanoi","Vietnam"),("Tokyo","Japan"),("Seoul","South Korea"),("Taipei","Taiwan"),("Delhi","India"),("Dubai","United Arab Emirates"),("Istanbul","Turkey"),("Berlin","Germany"),("Paris","France"),("London","United Kingdom"),("Amsterdam","Netherlands"),("Madrid","Spain"),("Milan","Italy"),("New York","United States"),("Toronto","Canada"),("Mexico City","Mexico"),("Sao Paulo","Brazil"),("Sydney","Australia"),("Nairobi","Kenya"),("Cape Town","South Africa"),("Lagos","Nigeria"),("Auckland","New Zealand")]
SECTORS = ["restaurant","hotel","beauty salon","fitness studio","dental clinic","real estate agency","marketing agency","accounting firm","law firm","e-commerce brand","fashion store","furniture store","car dealership","travel agency","education company","software company","IT services company","construction company","interior design studio","event organizer","logistics company","manufacturer","medical clinic","coworking space","consulting firm","retail shop","photography studio","wedding vendor"]
DOMAINS = [("instagram.com","Instagram"),("facebook.com","Facebook"),("linkedin.com/company","LinkedIn"),("tiktok.com","TikTok")]
LANGUAGE = {
"Indonesia":("Indonesian","Halo tim {name}, saya menemukan profil publik {name} di {city}, {country}. Ada kemungkinan saya dapat membantu meningkatkan {service} agar {benefit}. Apakah saya boleh mengirimkan beberapa ide yang relevan? Jika tidak sesuai, beri tahu saya dan saya tidak akan menindaklanjuti."),
"Japan":("Japanese","{name} ご担当者様、突然のご連絡失礼いたします。公開情報を拝見し、{service} の改善を通じて {benefit} に貢献できる可能性があると感じました。具体的なアイデアをお送りしてもよろしいでしょうか。ご不要でしたらお知らせください。"),
"South Korea":("Korean","{name} 담당자님 안녕하세요. 공개된 정보를 살펴보던 중 연락드립니다. {service} 개선을 통해 {benefit}에 도움을 드릴 수 있을 것 같아 맞춤형 아이디어를 공유드려도 될지 문의드립니다. 원치 않으시면 알려주세요."),
"China":("Chinese","{name} 团队您好！我在研究 {city} 的企业时看到了贵公司的公开资料。优化 {service} 或许能帮助贵公司实现 {benefit}。方便的话，我可以发送几条建议吗？如不需要，请告知，我不会继续联系。"),
"Taiwan":("Chinese","{name} 團隊您好！我在研究 {city} 的企業時看到了貴公司的公開資料。改善 {service} 或許能協助貴公司達成 {benefit}。方便的話，我可以分享幾個建議嗎？若不需要請告知，我不會繼續聯絡。"),
"Thailand":("Thai","สวัสดีทีมงาน {name} ผมพบข้อมูลสาธารณะของธุรกิจคุณใน {city} อาจมีโอกาสปรับปรุง {service} เพื่อช่วย {benefit} ขออนุญาตส่งแนวคิดที่เหมาะกับธุรกิจได้ไหมครับ หากไม่สะดวกแจ้งได้เลยครับ"),
"Vietnam":("Vietnamese","Xin chào đội ngũ {name}, tôi tìm thấy thông tin công khai của doanh nghiệp tại {city}. Có thể có cơ hội cải thiện {service} để hỗ trợ {benefit}. Tôi có thể gửi một vài ý tưởng phù hợp không? Nếu không phù hợp, vui lòng cho tôi biết."),
"Germany":("German","Guten Tag, liebes Team von {name}. Bei meiner Recherche zu Unternehmen in {city}, {country} bin ich auf Ihr öffentliches Profil gestoßen. Möglicherweise lässt sich {service} verbessern, um {benefit}. Darf ich Ihnen einige Ideen schicken? Falls nicht, geben Sie mir bitte Bescheid."),
"France":("French","Bonjour à l’équipe de {name}, j’ai découvert votre profil public à {city}, {country}. Il pourrait être intéressant d’améliorer {service} afin de {benefit}. Puis-je vous envoyer quelques idées adaptées ? Si cela ne vous intéresse pas, dites-le-moi et je ne vous relancerai pas."),
"Spain":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Mexico":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas? Si no les interesa, avísenme y no insistiré."),
"Brazil":("Portuguese","Olá, equipe da {name}. Encontrei o perfil público da empresa em {city}, {country}. Pode haver uma oportunidade de melhorar {service} e ajudar {benefit}. Posso compartilhar algumas ideias? Se não fizer sentido, é só avisar e não voltarei a contactar."),
"Italy":("Italian","Buongiorno team di {name}, ho trovato il vostro profilo pubblico a {city}, {country}. Potrebbe esserci un'opportunità per migliorare {service} e contribuire a {benefit}. Posso condividere qualche idea? Se non vi interessa, fatemelo sapere."),
"Netherlands":("Dutch","Hallo team van {name}, ik kwam uw openbare bedrijfsprofiel tegen in {city}, {country}. Mogelijk is er een kans om {service} te verbeteren en te helpen bij {benefit}. Mag ik enkele ideeën delen? Laat het weten als dit niet relevant is."),
"Malaysia":("Malay","Salam pasukan {name}, saya menemui profil perniagaan awam anda di {city}, {country}. Mungkin ada peluang untuk menambah baik {service} bagi membantu {benefit}. Bolehkah saya berkongsi beberapa idea yang sesuai? Jika tidak relevan, beritahu saya dan saya tidak akan menghubungi lagi."),
"United Arab Emirates":("Arabic","مرحباً بفريق {name}، اطّلعت على المعلومات العامة لنشاطكم في {city}، {country}. قد تكون هناك فرصة لتحسين {service} للمساعدة في {benefit}. هل يناسبكم أن أشارك بعض الأفكار المخصصة؟ إذا لم يكن ذلك مناسباً، أخبروني ولن أتابع التواصل."),
"Saudi Arabia":("Arabic","مرحباً بفريق {name}، اطّلعت على المعلومات العامة لنشاطكم في {city}، {country}. قد تكون هناك فرصة لتحسين {service} للمساعدة في {benefit}. هل يناسبكم أن أشارك بعض الأفكار المخصصة؟ إذا لم يكن ذلك مناسباً، أخبروني ولن أتابع التواصل."),
"Egypt":("Arabic","مرحباً بفريق {name}، وجدت ملف نشاطكم المنشور علناً في {city}، {country}. قد توجد فرصة لتحسين {service} للمساعدة في {benefit}. هل يمكنني إرسال بعض الأفكار المناسبة لنشاطكم؟ إذا لم يكن ذلك مناسباً، أخبروني ولن أتابع التواصل."),
"Turkey":("Turkish","Merhaba {name} ekibi, {city}, {country} bölgesindeki işletmeleri araştırırken herkese açık işletme profilinizi buldum. {benefit} amacıyla {service} alanında bir iyileştirme fırsatı olabilir. İşletmenize özel birkaç fikir paylaşmam uygun olur mu? İlgilenmiyorsanız lütfen bildirin; tekrar iletişime geçmem."),
"Portugal":("Portuguese","Olá, equipa da {name}. Encontrei o perfil público da empresa em {city}, {country}. Pode haver uma oportunidade de melhorar {service} e ajudar {benefit}. Posso partilhar algumas ideias personalizadas? Se não for relevante, diga-me e não voltarei a contactar."),
"Argentina":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Colombia":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Chile":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Peru":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Morocco":("French","Bonjour à l’équipe de {name}, j’ai découvert votre profil public à {city}, {country}. Il pourrait être intéressant d’améliorer {service} afin de {benefit}. Puis-je vous envoyer quelques idées adaptées ? Si cela ne vous intéresse pas, dites-le-moi et je ne vous relancerai pas."),
"Singapore":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Philippines":("English","Hello {name} team, I found your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"India":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"United States":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"United Kingdom":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Canada":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Australia":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"New Zealand":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Kenya":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"South Africa":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Nigeria":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Ghana":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Saudi Arabia":("Arabic","مرحباً بفريق {name}، اطّلعت على المعلومات العامة لنشاطكم في {city}، {country}. قد تكون هناك فرصة لتحسين {service} للمساعدة في {benefit}. هل يناسبكم أن أشارك بعض الأفكار المخصصة؟ إذا لم يكن ذلك مناسباً، أخبروني ولن أتابع التواصل."),

}
DEFAULT = ("English","Hello {name} team, I came across your public business profile while researching companies in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up.")
OSM = [
("Jakarta","Indonesia",-6.2088,106.8456),("Bandung","Indonesia",-6.9175,107.6191),("Surabaya","Indonesia",-7.2575,112.7521),("Yogyakarta","Indonesia",-7.7956,110.3695),
("Kuala Lumpur","Malaysia",3.139,101.6869),("Singapore","Singapore",1.3521,103.8198),("Bangkok","Thailand",13.7563,100.5018),("Manila","Philippines",14.5995,120.9842),
("Tokyo","Japan",35.6762,139.6503),("Delhi","India",28.6139,77.209),("Dubai","United Arab Emirates",25.2048,55.2708),("London","United Kingdom",51.5072,-0.1276),
("Berlin","Germany",52.52,13.405),("Paris","France",48.8566,2.3522),("New York","United States",40.7128,-74.006),("Toronto","Canada",43.6532,-79.3832),
("Sydney","Australia",-33.8688,151.2093),("Sao Paulo","Brazil",-23.5505,-46.6333)]
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def s(v,n=1000): return re.sub(r"\s+"," ",str(v or "")).strip()[:n]
def url(v):
    v=s(v,500).strip("()[]{}<>,.;\"'")
    if not v: return ""
    if not v.startswith(("http://","https://")): v="https://"+v
    p=urlparse(v)
    return v if p.netloc and "." in p.netloc else ""
def host(v): return (urlparse(v).hostname or "").lower().removeprefix("www.")
def social_type(v):
    h=host(v)
    for d,k in SOCIAL.items():
        if h==d or h.endswith("."+d): return k
    return ""
def urls(text):
    return list(dict.fromkeys(url(x) for x in re.findall(r"https?://[^\s<>\"']+",str(text or ""),re.I) if url(x)))
def socials(text):
    d={k:"" for k in ["instagram","facebook","linkedin","tiktok","other_social"]}
    for u in urls(text):
        k=social_type(u)
        if k and not d[k]: d[k]=u
    return d
def whatsapp(text):
    for u in urls(text):
        if host(u) in ("wa.me","api.whatsapp.com","web.whatsapp.com","whatsapp.com") or host(u).endswith(".whatsapp.com"): return u
    return ""
def mail(text):
    m=re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",str(text or ""))
    return m[0] if m else ""
def phone(text):
    for x in re.findall(r"\+?\d[\d ()-]{7,}\d",str(text or "")):
        if 8<=len(re.sub(r"\D","",x))<=15: return x
    return ""
def pid(name,country,key): return hashlib.sha256(f"{name.lower().strip()}|{country.lower().strip()}|{key.lower().strip()}".encode()).hexdigest()[:18]
def make_record(name,country,city,industry,website,wa,phone_v,email,soc,source,source_name,evidence):
    if not wa and not any(soc.values()): return None
    identity_scope=f"{city}|{industry}"
    return {"prospect_id":pid(name,country,identity_scope),"company_name":name,"country":country,"city":city,"industry":industry,
      "website":website,"whatsapp_url":wa,"public_phone":phone_v,"public_email":email,**soc,
      "source_url":source,"source_name":source_name,"evidence":s(evidence,1200),"discovered_at_utc":now(),
      "outreach_language":"","need_audit":"","recommended_service":"","prospect_score":0,"prospect_grade":"MEDIUM",
      "grade_reason":"","outreach_dm":"","outreach_email_subject":"","outreach_email_body":"","outreach_whatsapp":"","data_quality":"Public source; verify before contact"}
def tavily(key,query):
    r=requests.post("https://api.tavily.com/search",json={"api_key":key,"query":query,"search_depth":"advanced","topic":"general","max_results":10,"include_answer":False,"include_raw_content":False},headers={"User-Agent":UA},timeout=35)
    if r.status_code==429: L.warning("Tavily rate limit/quota reached"); return []
    r.raise_for_status(); return r.json().get("results",[])
def discover_web(key,wanted):
    out={}
    if not key: L.warning("TAVILY_API_KEY missing; only OSM discovery is available"); return []
    dt=datetime.now(TZ); start=(dt.timetuple().tm_yday*5+dt.hour//6*7)%len(REGIONS)
    for i in range(min(12,max(4,(wanted+9)//10))):
        city,country=REGIONS[(start+i)%len(REGIONS)]; sector=SECTORS[(dt.timetuple().tm_yday*3+(dt.hour//6)*5+i*7)%len(SECTORS)]
        domain,platform=DOMAINS[(i+dt.hour//6)%len(DOMAINS)]
        query=f'site:{domain} "{sector}" "{city}" "{country}" business company official contact'
        try: results=tavily(key,query)
        except Exception as e: L.warning("Tavily error %s: %s",platform,s(e,180)); continue
        L.info("Tavily %s: %s result(s) for %s, %s",platform,len(results),city,country)
        for z in results:
            u=url(z.get("url","")); title=s(z.get("title"),160); snippet=s(z.get("content"),900)
            if not u or not title or title.lower() in {"instagram","facebook","linkedin","tiktok","home","homepage","log in","sign up"}: continue
            combined=f"{title}. {snippet}. {u}"; soc=socials(combined); sk=social_type(u)
            if sk in soc: soc[sk]=soc[sk] or u
            wa=whatsapp(combined)
            if not wa and not any(soc.values()): continue
            name=re.sub(r"\s*[|–-]\s*(Instagram|Facebook|LinkedIn|TikTok|Official.*)$","",title,flags=re.I).strip()
            name=re.sub(r"\s*\(@[^)]*\)","",name).strip()
            if len(name)<2: continue
            website="" if sk else u
            row=make_record(name,country,city,sector,website,wa,phone(snippet),mail(combined),soc,u,f"Tavily Search / {platform}",f"Title: {title}. Snippet: {snippet}")
            if row: out.setdefault(row["prospect_id"],row)
        time.sleep(.25)
        if len(out)>=min(wanted*2,150): break
    return list(out.values())
def overpass_query(lat,lon):
    keys=["contact:instagram","instagram","contact:facebook","facebook","contact:linkedin","linkedin","contact:tiktok","tiktok","contact:whatsapp","whatsapp","contact:youtube","youtube"]
    sel="\n".join(f'nwr(around:9000,{lat},{lon})["name"]["{k}"];' for k in keys)
    return f"[out:json][timeout:30];(\n{sel}\n);out center tags 180;"
def discover_osm(wanted):
    out={}; dt=datetime.now(TZ); start=(dt.timetuple().tm_yday*3+dt.hour//6*5)%len(OSM)
    for city,country,lat,lon in [OSM[(start+i)%len(OSM)] for i in range(min(8,len(OSM)))]:
        try:
            r=requests.post("https://overpass-api.de/api/interpreter",data={"data":overpass_query(lat,lon)},headers={"User-Agent":UA},timeout=45)
            if r.status_code in (429,502,503,504): L.warning("Overpass HTTP %s at %s",r.status_code,city); continue
            r.raise_for_status(); els=r.json().get("elements",[])
        except Exception as e: L.warning("Overpass error at %s: %s",city,s(e,180)); continue
        L.info("OSM/Overpass: %s tagged record(s) around %s",len(els),city)
        for el in els:
            tags=el.get("tags",{}); name=s(tags.get("name"),160)
            if len(name)<2: continue
            soc={k:"" for k in ["instagram","facebook","linkedin","tiktok","other_social"]}; wa=""
            keys={"instagram":["contact:instagram","instagram"],"facebook":["contact:facebook","facebook"],"linkedin":["contact:linkedin","linkedin"],"tiktok":["contact:tiktok","tiktok"],"other_social":["contact:youtube","youtube","contact:x","twitter","x"]}
            for field,alts in keys.items():
                for k in alts:
                    raw=tags.get(k)
                    if raw:
                        v=url(str(raw))
                        if v and (social_type(v) or k in ("instagram","facebook","linkedin","tiktok","youtube","twitter","x")): soc[field]=soc[field] or v
            for k in ("contact:whatsapp","whatsapp"):
                raw=tags.get(k,"")
                if raw:
                    v=url(str(raw))
                    if v and ("whatsapp" in host(v) or host(v)=="wa.me"): wa=v
                    else:
                        digits=re.sub(r"\D","",str(raw))
                        if 8<=len(digits)<=15: wa="https://wa.me/"+digits
            website=url(tags.get("contact:website") or tags.get("website") or "")
            kind=tags.get("shop") or tags.get("office") or tags.get("craft") or tags.get("amenity") or tags.get("tourism") or tags.get("leisure") or "Business"
            osm_url=f"https://www.openstreetmap.org/{el.get('type','node')}/{el.get('id','')}"
            row=make_record(name,country,city,s(kind,100),website,wa,tags.get("contact:phone") or tags.get("phone",""),tags.get("contact:email") or tags.get("email",""),soc,osm_url,"OpenStreetMap / Overpass",json.dumps(tags,ensure_ascii=False))
            if row: out.setdefault(row["prospect_id"],row)
        time.sleep(2)
        if len(out)>=min(wanted*2,150): break
    return list(out.values())
def gemini(prompt,key,model):
    r=requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",params={"key":key},
       json={"contents":[{"role":"user","parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.25,"responseMimeType":"application/json"}},
       headers={"User-Agent":UA},timeout=45)
    if r.status_code==404: raise RuntimeError(f"Gemini model {model} not found; configure GEMINI_MODEL")
    if r.status_code==429: raise RuntimeError("Gemini API quota/rate limit hit")
    r.raise_for_status(); parts=r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[])
    text="".join(x.get("text","") for x in parts)
    text=re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$","",text.strip(),flags=re.I)
    a,b=text.find("{"),text.rfind("}")
    if a<0 or b<=a: raise RuntimeError("Gemini response was not JSON")
    return json.loads(text[a:b+1])
def template_fallback(p,err):
    lang,tmpl=LANGUAGE.get(p["country"],DEFAULT)
    service="social media planning, lead tracking, and customer inquiry automation"
    benefit="save response time and follow up with interested customers more consistently"
    draft=tmpl.format(name=p["company_name"],city=p["city"],country=p["country"],service=service,benefit=benefit)
    score=45+bool(p.get("whatsapp_url"))*12+bool(p.get("public_email"))*8+bool(p.get("website"))*8+sum(bool(p.get(k)) for k in ("instagram","facebook","linkedin","tiktok"))*3
    score=min(78,score); p.update(outreach_language=lang,need_audit="Source evidence is too limited for a confident company-specific diagnosis. Verify the business profile and identify a real service gap before contacting. AI fallback: "+s(err,250),recommended_service="Possible services to validate: social media planning, inquiry automation, and lead tracking.",prospect_score=score,prospect_grade="RECOMMENDED" if score>=75 else ("MEDIUM" if score>=45 else "LOW"),grade_reason="Fallback score based on public channels, not evidence of buying intent; manual review required.",outreach_dm=draft,outreach_whatsapp=draft,outreach_email_subject=f"Ideas for {p['company_name']}",outreach_email_body=draft,data_quality=p.get("data_quality","")+"; fallback analysis")
def analyze(p,key,model):
    lang,_=LANGUAGE.get(p["country"],DEFAULT)
    facts={k:p.get(k,"") for k in ("company_name","country","city","industry","website","whatsapp_url","public_email","public_phone","instagram","facebook","linkedin","tiktok","other_social","source_url","source_name","evidence")}
    prompt=f"""You are a cautious B2B prospect researcher for an AI automation/digital services agency. Analyze ONLY supplied public evidence; never invent business needs, budget, buying intent, results, or facts. If evidence is thin, say that. JSON only with: need_audit (2-4 sentences, distinguish observations/hypotheses), recommended_service (1-3 specific and plausible services, not a confirmed need), prospect_score (integer 0-100; evidence specificity 35%, fit 25%, public contact usability 25%, data quality 15%), prospect_grade (RECOMMENDED for 75-100, MEDIUM for 45-74, LOW for 0-44), grade_reason, outreach_language (use {lang} unless evidence suggests another language), outreach_dm, outreach_email_subject, outreach_email_body, outreach_whatsapp. Write all four messages in outreach_language; keep first contact polite and concise, personalize only with verified info, ask permission to share tailored ideas, include a brief opt-out, and do not imply prior contact or send anything automatically. Company facts: {json.dumps(facts,ensure_ascii=False)}"""
    try:
        d=gemini(prompt,key,model); score=max(0,min(100,int(float(d.get("prospect_score",45)))))
        grade="RECOMMENDED" if score>=75 else ("MEDIUM" if score>=45 else "LOW")
        for k in ("need_audit","recommended_service","grade_reason","outreach_dm","outreach_email_subject","outreach_email_body","outreach_whatsapp","outreach_language"): p[k]=s(d.get(k),2500)
        p["prospect_score"]=score; p["prospect_grade"]=grade
        if not p["need_audit"] or not p["outreach_dm"]: raise ValueError("Required AI fields missing")
    except Exception as e:
        L.warning("AI fallback for %s: %s",p["company_name"],s(e,180)); template_fallback(p,str(e))
def sheet(url_,token,payload):
    r=requests.post(url_,json={"token":token,**payload},headers={"User-Agent":UA},timeout=45); r.raise_for_status()
    d=r.json()
    if not d.get("ok"): raise RuntimeError("Sheet endpoint error: "+s(d,300))
    return d
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); args=ap.parse_args()
    tk=os.getenv("TAVILY_API_KEY","").strip(); gk=os.getenv("GEMINI_API_KEY","").strip()
    wh=os.getenv("SHEET_WEBHOOK_URL","").strip(); token=os.getenv("WEBHOOK_TOKEN","").strip()
    model=os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite").strip()
    try: target=max(1,min(500,int(os.getenv("DAILY_TARGET","100"))))
    except ValueError: target=100
    if not gk: L.error("GEMINI_API_KEY is required"); return 2
    if not args.dry_run and (not wh or not token): L.error("SHEET_WEBHOOK_URL and WEBHOOK_TOKEN are required"); return 2
    daily=0
    if not args.dry_run:
        try: daily=int(sheet(wh,token,{"action":"stats"}).get("daily_count",0))
        except Exception as e: L.error("Could not read Sheet stats: %s",s(e,250)); return 3
        L.info("Jakarta daily total %d/%d",daily,target)
        if daily>=target: L.info("Daily target already met"); return 0
    wanted=target if args.dry_run else target-daily
    pool={}
    for batch in (discover_web(tk,wanted),discover_osm(wanted)):
        for p in batch: pool.setdefault(p["prospect_id"],p)
    rows=list(pool.values())
    rows.sort(key=lambda p:(bool(p["whatsapp_url"]),bool(p["public_email"]),sum(bool(p[k]) for k in ("instagram","facebook","linkedin","tiktok","other_social")),bool(p["website"])),reverse=True)
    if not args.dry_run: rows=rows[:min(200,(target-daily)*2)]
    L.info("Qualified distinct prospects with a public WhatsApp/social profile: %d",len(rows))
    for i,p in enumerate(rows):
        analyze(p,gk,model)
        if i<len(rows)-1: time.sleep(.2)
    if args.dry_run:
        print(json.dumps(rows[:20],ensure_ascii=False,indent=2)); L.info("Dry run only; no rows uploaded"); return 0
    for start in range(0,len(rows),25):
        try:
            result=sheet(wh,token,{"action":"append","prospects":rows[start:start+25],"run_id":now()})
            daily=int(result.get("daily_count",daily+int(result.get("inserted",0))))
            L.info("Inserted %s; daily count %d/%d",result.get("inserted",0),daily,target)
            if daily>=target: break
        except Exception as e: L.error("Google Sheets append failed: %s",s(e,300)); return 4
    if daily<target: L.warning("TARGET GAP: %d records short today; next scheduled run will continue.",target-daily)
    return 0
if __name__=="__main__": sys.exit(main())
